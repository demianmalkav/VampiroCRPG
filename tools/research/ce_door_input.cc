// Private laboratory input adapter; no game implementation or assets included.
// Compiled against clean CE headers and offsets extracted from the exact ELF.
// Only substitutes SDL relative mouse input. Native query calls are read-only.
#include <SDL.h>
#include <dlfcn.h>
#include <link.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include "obj_types.h"
#include "geometry.h"
#include "ce_probe_offsets.h"

static uintptr_t base;
static int find_base(dl_phdr_info* info, size_t, void*) {
    if (!info->dlpi_name || !*info->dlpi_name) base = info->dlpi_addr;
    return 0;
}
template<class T> static T at(uintptr_t offset) { return reinterpret_cast<T>(base + offset); }
static void object_json(FILE* out, const fallout::Object* obj) {
    if (!obj) { std::fputs("null", out); return; }
    std::fprintf(out, "{\"id\":%d,\"tile\":%d,\"pid\":%u,\"fid\":%u,\"flags\":%u,\"frame\":%d,\"rotation\":%d,\"elevation\":%d,\"x\":%d,\"y\":%d}",
        obj->id, obj->tile, unsigned(obj->pid), unsigned(obj->fid), unsigned(obj->flags),
        obj->frame, obj->rotation, obj->elevation, obj->x, obj->y);
}


static fallout::Object* reference_door() {
    auto table = at<fallout::ObjectListNode**>(OFF_OBJECT_TABLE);
    for (auto n=table[15710]; n; n=n->next)
        if (n->obj->id==26 && n->obj->pid==33555281 && n->obj->elevation==0) return n->obj;
    return nullptr;
}
static void door_json(FILE* out) {
    auto door=reference_door();
    std::fputs(",\"door\":",out); object_json(out,door);
    if (!door) return;
    fallout::Rect rect;
    at<void (*)(fallout::Object*,fallout::Rect*)>(OFF_RECT)(door,&rect);
    std::fprintf(out,",\"door_open_flags\":%d,\"door_rect\":[%d,%d,%d,%d]",door->data.scenery.door.openFlags,rect.left,rect.top,rect.right,rect.bottom);
    std::fputs(",\"door_blocker\":",out);
    auto dude=*at<fallout::Object**>(OFF_DUDE);
    object_json(out,at<fallout::Object* (*)(fallout::Object*,int,int)>(OFF_BLOCKING)(dude,door->tile,door->elevation));
    std::fputs(",\"selected_object\":",out);
    object_json(out,at<fallout::Object* (*)(int,bool,int)>(OFF_SELECT)(-1,true,door->elevation));
}

static void record_tile_transition(long sequence) {
    const char* path = std::getenv("CE_PROBE_MOTION");
    if (!path) return;
    static int last_tile = -1, last_frame=-1, last_fid=-1, last_x=-999, last_y=-999, door_frame=-1, door_flags=-1, door_open=-1;
    auto dude = *at<fallout::Object**>(OFF_DUDE);
    if (!dude || dude->tile < 0) return;
    auto door=reference_door();
    if (!door) return;
    if (dude->tile==last_tile && dude->frame==last_frame && dude->fid==last_fid && dude->x==last_x && dude->y==last_y && door->frame==door_frame && int(door->flags)==door_flags && door->data.scenery.door.openFlags==door_open) return;
    last_frame=dude->frame;last_fid=dude->fid;last_x=dude->x;last_y=dude->y;
    door_frame=door->frame;door_flags=int(door->flags);door_open=door->data.scenery.door.openFlags;
    last_tile = dude->tile;
    auto blocking = at<fallout::Object* (*)(fallout::Object*, int, int)>(OFF_BLOCKING);
    FILE* out = std::fopen(path, "a");
    if (!out) return;
    std::fprintf(out, "{\"sdl_tick_ms\":%u,\"input_sequence\":%ld,\"dude\":", SDL_GetTicks(), sequence);
    object_json(out, dude);
    std::fputs(",\"blocker_at_actor\":", out);
    object_json(out, blocking(dude, dude->tile, dude->elevation));
    door_json(out);
    std::fputs("}\n", out);
    std::fclose(out);
}

extern "C" Uint32 SDL_GetRelativeMouseState(int* x, int* y) {
    using Mouse = Uint32 (*)(int*, int*);
    static Mouse real = reinterpret_cast<Mouse>(dlsym(RTLD_NEXT, "SDL_GetRelativeMouseState"));
    static long previous = -1;
    static unsigned held = 0;
    Uint32 original = real(x, y);
    const char* command = std::getenv("CE_PROBE_COMMAND");
    const char* receipt = std::getenv("CE_PROBE_RECEIPT");
    if (!command || !receipt) return original;
    FILE* in = std::fopen(command, "r");
    long sequence;
    int target;
    unsigned buttons;
    int input_x=0,input_y=0;
    int count = in ? std::fscanf(in, "%ld %d %u %d %d", &sequence, &target, &buttons,&input_x,&input_y) : 0;
    if (in) std::fclose(in);
    if (count < 3) return original;
    *x = *y = 0;
    if (!base) dl_iterate_phdr(find_base, nullptr);
    record_tile_transition(sequence);
    if (sequence == previous) return held;
    previous = sequence;
    held = buttons;
    auto dude = *at<fallout::Object**>(OFF_DUDE);
    int elevation = *at<int*>(OFF_ELEVATION);
    int cx = *at<int*>(OFF_CURSOR_X) + *at<int*>(OFF_HOT_X);
    int cy = *at<int*>(OFF_CURSOR_Y) + *at<int*>(OFF_HOT_Y);
    auto project = at<int (*)(int, int*, int*, int)>(OFF_PROJECT);
    auto unproject = at<int (*)(int, int, int, bool)>(OFF_UNPROJECT);
    auto neighbor = at<int (*)(int, int, int)>(OFF_NEIGHBOR);
    auto blocking = at<fallout::Object* (*)(fallout::Object*, int, int)>(OFF_BLOCKING);
    int px = cx, py = cy, roundtrip = -1;
    if (target >= 0 && project(target, &px, &py, elevation) == 0) {
        px += 16;
        py += 8;
        roundtrip = unproject(px, py, elevation, false);
        *x = px - cx;
        *y = py - cy;
    }
    if (target == -3 && count==5) { px=input_x;py=input_y;*x=px-cx;*y=py-cy; }
    FILE* out = std::fopen(receipt, "w");
    if (!out) return held;
    std::fprintf(out, "{\"sequence\":%ld,\"requested_tile\":%d,\"buttons\":%u,\"cursor_before\":[%d,%d],\"cursor_tile_before\":%d,\"projected_center\":[%d,%d],\"roundtrip_tile\":%d,\"mouse_mode\":%d,\"dude\":",
        sequence, target, buttons, cx, cy, unproject(cx, cy, elevation, false), px, py, roundtrip, *at<int*>(OFF_MOUSE_MODE));
    object_json(out, dude);
    std::fputs(",\"neighbors\":[", out);
    for (int d = 0; d < 6; ++d) std::fprintf(out, "%s%d", d ? "," : "", neighbor(dude->tile, d, 1));
    std::fputs("],\"blocker\":", out);
    object_json(out, target >= 0 ? blocking(dude, target, elevation) : nullptr);
    if (target == -2) {
        auto table = at<fallout::ObjectListNode**>(OFF_OBJECT_TABLE);
        std::fputs(",\"visible_tile_objects\":[", out);
        bool comma = false;
        for (int tile = 0; tile < 40000; ++tile) {
            int sx, sy;
            project(tile, &sx, &sy, elevation);
            if (sx < -32 || sx > 800 || sy < -32 || sy > 500) continue;
            for (auto node = table[tile]; node; node = node->next) {
                auto obj = node->obj;
                if (obj->elevation != elevation || (obj->flags & fallout::OBJECT_HIDDEN)) continue;
                if (comma) std::fputc(',', out);
                object_json(out, obj);
                comma = true;
            }
        }
        std::fputc(']', out);
    }
    door_json(out);
    std::fprintf(out, ",\"native_Object_bytes\":%zu,\"native_pid_offset\":%zu}\n", sizeof(fallout::Object), offsetof(fallout::Object,pid));
    std::fclose(out);
    return held;
}
