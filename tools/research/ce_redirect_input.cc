// Private redirection pose/input probe; no game implementation or assets included.
// Compiled against clean CE headers and offsets extracted from the exact ELF.
// Only substitutes SDL relative mouse input. Native query calls are read-only.
#include <SDL.h>
#include <dlfcn.h>
#include <link.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include "obj_types.h"
#include "ce_probe_offsets.h"

static uintptr_t base;
static int find_base(dl_phdr_info* info, size_t, void*) {
    if (!info->dlpi_name || !*info->dlpi_name) base = info->dlpi_addr;
    return 0;
}
template<class T> static T at(uintptr_t offset) { return reinterpret_cast<T>(base + offset); }
static void anchor_json(FILE* out, const fallout::Object* obj) {
    int x=0,y=0;
    auto project=at<int (*)(int,int*,int*,int)>(OFF_PROJECT);
    if (!obj || obj->tile<0 || project(obj->tile,&x,&y,obj->elevation)!=0) {
        std::fputs("null",out); return;
    }
    std::fprintf(out,"[%d,%d]",x+16+obj->x,y+8+obj->y);
}
static void object_json(FILE* out, const fallout::Object* obj) {
    if (!obj) { std::fputs("null", out); return; }
    std::fprintf(out, "{\"id\":%d,\"tile\":%d,\"pid\":%u,\"fid\":%u,\"flags\":%u,\"frame\":%d,\"rotation\":%d,\"elevation\":%d,\"x\":%d,\"y\":%d}",
        obj->id, obj->tile, unsigned(obj->pid), unsigned(obj->fid), unsigned(obj->flags),
        obj->frame, obj->rotation, obj->elevation, obj->x, obj->y);
}

static void record_pose(long sequence) {
    const char* path = std::getenv("CE_PROBE_MOTION");
    if (!path) return;
    static int last[7]={-1,-1,-1,-1,-1,-1,-1};
    static long last_sequence=-1;
    auto dude = *at<fallout::Object**>(OFF_DUDE);
    if (!dude || dude->tile < 0) return;
    int pose[7]={dude->tile,dude->x,dude->y,dude->frame,dude->fid,dude->rotation,dude->elevation};
    bool changed=sequence!=last_sequence;
    for(int i=0;i<7;++i) if(pose[i]!=last[i]) changed=true;
    if(!changed) return;
    last_sequence=sequence;
    for(int i=0;i<7;++i) last[i]=pose[i];
    auto blocking = at<fallout::Object* (*)(fallout::Object*, int, int)>(OFF_BLOCKING);
    FILE* out = std::fopen(path, "a");
    if (!out) return;
    std::fprintf(out, "{\"sdl_tick_ms\":%u,\"input_sequence\":%ld,\"dude\":", SDL_GetTicks(), sequence);
    object_json(out, dude);
    std::fputs(",\"anchor_xy\":",out); anchor_json(out,dude);
    std::fputs(",\"blocker_at_actor\":", out);
    object_json(out, blocking(dude, dude->tile, dude->elevation));
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
    int count = in ? std::fscanf(in, "%ld %d %u", &sequence, &target, &buttons) : 0;
    if (in) std::fclose(in);
    if (count != 3) return original;
    *x = *y = 0;
    if (!base) dl_iterate_phdr(find_base, nullptr);
    record_pose(sequence);
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
    FILE* out = std::fopen(receipt, "w");
    if (!out) return held;
    std::fprintf(out, "{\"sequence\":%ld,\"requested_tile\":%d,\"buttons\":%u,\"cursor_before\":[%d,%d],\"cursor_tile_before\":%d,\"projected_center\":[%d,%d],\"roundtrip_tile\":%d,\"mouse_mode\":%d,\"dude\":",
        sequence, target, buttons, cx, cy, unproject(cx, cy, elevation, false), px, py, roundtrip, *at<int*>(OFF_MOUSE_MODE));
    object_json(out, dude);
    std::fprintf(out,",\"sdl_tick_ms\":%u,\"anchor_xy\":",SDL_GetTicks()); anchor_json(out,dude);
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
    std::fprintf(out, ",\"native_Object_bytes\":%zu,\"native_pid_offset\":%zu}\n", sizeof(fallout::Object), offsetof(fallout::Object,pid));
    std::fclose(out);
    return held;
}
