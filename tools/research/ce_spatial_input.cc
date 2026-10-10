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
#include "object.h"
#include <vector>
#include <set>
#include <string>
#include "ce_probe_offsets.h"

static uintptr_t base;
static int find_base(dl_phdr_info* info, size_t, void*) {
    if (!info->dlpi_name || !*info->dlpi_name) base = info->dlpi_addr;
    return 0;
}
template<class T> static T at(uintptr_t offset) { return reinterpret_cast<T>(base + offset); }
static void object_json(FILE* out, const fallout::Object* obj) {
    if (!obj) { std::fputs("null", out); return; }
    std::fprintf(out, "{\"id\":%d,\"tile\":%d,\"pid\":%u,\"fid\":%u,\"flags\":%u,\"frame\":%d,\"rotation\":%d,\"elevation\":%d,\"x\":%d,\"y\":%d,\"data_flags\":%d,\"inventory_length\":%d}",
        obj->id, obj->tile, unsigned(obj->pid), unsigned(obj->fid), unsigned(obj->flags),
        obj->frame, obj->rotation, obj->elevation, obj->x, obj->y, obj->data.flags, obj->data.inventory.length);
}



static void hits_json(FILE* out,int x,int y,int elevation) {
    fallout::ObjectWithFlags* entries=nullptr;
    int count=at<int (*)(int,int,int,int,fallout::ObjectWithFlags**)>(OFF_HITS)(x,y,elevation,-1,&entries);
    std::fputc('[',out);
    for(int i=0;i<count;i++) {
        if(i)std::fputc(',',out);
        std::fprintf(out,"{\"hit_flags\":%d,\"object\":",entries[i].flags);object_json(out,entries[i].object);std::fputc('}',out);
    }
    std::fputc(']',out);
    if(count)at<void (*)(fallout::ObjectWithFlags**)>(OFF_FREE_HITS)(&entries);
}
static void point_json(FILE* out,int x,int y,int elevation) {
    std::fprintf(out,"{\"xy\":[%d,%d],\"roof\":%d,\"egg_flags\":%d,\"hits\":",x,y,
      at<int (*)(int,int,int)>(OFF_ROOF)(x,y,elevation),
      at<int (*)(fallout::Object*,int,int)>(OFF_INTERSECT)(*at<fallout::Object**>(OFF_EGG),x,y));
    hits_json(out,x,y,elevation);std::fputc('}',out);
}
static void spatial_json(FILE* out,int cx,int cy,int elevation) {
    std::fputs(",\"cursor_point\":",out);point_json(out,cx,cy,elevation);
    auto dude=*at<fallout::Object**>(OFF_DUDE);if(!dude)return;
    fallout::Rect r;at<void (*)(fallout::Object*,fallout::Rect*)>(OFF_RECT)(dude,&r);
    std::fprintf(out,",\"actor_rect\":[%d,%d,%d,%d],\"actor_points\":[",r.left,r.top,r.right,r.bottom);
    for(int i=1;i<=3;i++){if(i>1)std::fputc(',',out);point_json(out,(r.left+r.right)/2,r.top+(r.bottom-r.top)*i/4,elevation);}
    std::fputc(']',out);
}
static void scan_json(FILE* out,int elevation) {
    std::fputs(",\"scan_points\":[",out);bool comma=false;int accepted=0;
    std::set<std::string> seen;
    for(int y=12;y<490 && accepted<80;y+=6)for(int x=8;x<795 && accepted<80;x+=6) {
        fallout::ObjectWithFlags* entries=nullptr;
        int count=at<int (*)(int,int,int,int,fallout::ObjectWithFlags**)>(OFF_HITS)(x,y,elevation,-1,&entries);
        std::vector<fallout::ObjectWithFlags> real;
        for(int i=0;i<count;i++)if(entries[i].object->pid>=0 && ((entries[i].object->fid>>24)&15)<=3)real.push_back(entries[i]);
        if(count)at<void (*)(fallout::ObjectWithFlags**)>(OFF_FREE_HITS)(&entries);
        if(real.size()<2)continue;
        auto a=real[real.size()-1],b=real[real.size()-2];
        std::string key=std::to_string(a.object->pid)+":"+std::to_string(a.object->tile)+":"+std::to_string(a.flags)+"/"+std::to_string(b.object->pid)+":"+std::to_string(b.object->tile)+":"+std::to_string(b.flags)+":"+std::to_string(at<int (*)(int,int,int)>(OFF_ROOF)(x,y,elevation));
        if(!seen.insert(key).second)continue;
        if(comma)std::fputc(',',out);point_json(out,x,y,elevation);comma=true;accepted++;
    }
    std::fputc(']',out);
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


static fallout::Object* reference_locker() {
    auto table=at<fallout::ObjectListNode**>(OFF_OBJECT_TABLE);
    int tile=std::atoi(std::getenv("CE_CONTAINER_TILE")),id=std::atoi(std::getenv("CE_CONTAINER_ID")),pid=std::atoi(std::getenv("CE_CONTAINER_PID"));
    for(auto n=table[tile];n;n=n->next)
        if(n->obj->id==id && n->obj->pid==pid && n->obj->elevation==0)return n->obj;
    return nullptr;
}
static bool inventory_visible() {
    return *at<bool*>(OFF_INV_INIT) && at<unsigned char* (*)(int)>(OFF_WINDOW_BUFFER)(*at<int*>(OFF_INV_WINDOW))!=nullptr;
}
static void inventory_json(FILE* out,const fallout::Object* obj) {
    std::fputc('[',out);
    if(obj && obj->data.inventory.length>=0 && obj->data.inventory.length<=64) {
        for(int i=0;i<obj->data.inventory.length;i++) {
            auto slot=obj->data.inventory.items[i];
            if(i)std::fputc(',',out);
            std::fprintf(out,"{\"quantity\":%d,\"object\":",slot.quantity);object_json(out,slot.item);
            std::fputs(",\"owner\":",out);object_json(out,slot.item->owner);std::fputc('}',out);
        }
    }
    std::fputc(']',out);
}
static void locker_json(FILE* out) {
    auto locker=reference_locker();
    auto dude=*at<fallout::Object**>(OFF_DUDE);
    std::fputs(",\"locker\":",out);object_json(out,locker);
    if(!locker)return;
    fallout::Rect rect;at<void (*)(fallout::Object*,fallout::Rect*)>(OFF_RECT)(locker,&rect);
    std::fprintf(out,",\"locker_rect\":[%d,%d,%d,%d],\"locker_data_flags\":%d,\"locker_distance\":%d,\"inventory_visible\":%s,\"inventory_window\":%d,\"monitor_start\":%d",rect.left,rect.top,rect.right,rect.bottom,locker->data.flags,at<int (*)(fallout::Object*,fallout::Object*)>(OFF_DISTANCE)(dude,locker),inventory_visible()?"true":"false",*at<int*>(OFF_INV_WINDOW),*at<int*>(OFF_MONITOR_START));
    std::fputs(",\"inventory_target\":",out);object_json(out,inventory_visible()?*at<fallout::Object**>(OFF_INV_TARGET):nullptr);
    std::fputs(",\"locker_inventory\":",out);inventory_json(out,locker);
    std::fputs(",\"actor_inventory\":",out);inventory_json(out,dude);
    int start=*at<int*>(OFF_MONITOR_START),cap=*at<int*>(OFF_MONITOR_CAP);
    std::fputs(",\"monitor_recent_hex\":[",out);
    if(cap>0 && cap<=100)for(int j=2;j>0;j--) {
        auto line=at<unsigned char*>(OFF_MONITOR_LINES)+((start+cap-j)%cap)*80;
        if(j!=2)std::fputc(',',out);std::fputc('"',out);
        for(int k=0;k<80 && line[k];k++)std::fprintf(out,"%02x",line[k]);
        std::fputc('"',out);
    }
    std::fputc(']',out);
}

static void record_tile_transition(long sequence) {
    const char* path = std::getenv("CE_PROBE_MOTION");
    if (!path) return;
    static int last_locker_frame=-1,last_inventory=-1,last_monitor=-1;
    static int last_tile = -1, last_frame=-1, last_fid=-1, last_x=-999, last_y=-999, door_frame=-1, door_flags=-1, door_open=-1;
    auto dude = *at<fallout::Object**>(OFF_DUDE);
    if (!dude || dude->tile < 0) return;
    auto door=reference_door();
    if (!door) return;
    auto locker=reference_locker();
    int lf=locker?locker->frame:-1,iv=inventory_visible(),ms=*at<int*>(OFF_MONITOR_START);
    if (lf==last_locker_frame && iv==last_inventory && ms==last_monitor && dude->tile==last_tile && dude->frame==last_frame && dude->fid==last_fid && dude->x==last_x && dude->y==last_y && door->frame==door_frame && int(door->flags)==door_flags && door->data.scenery.door.openFlags==door_open) return;
    last_locker_frame=lf;last_inventory=iv;last_monitor=ms;
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
    door_json(out);locker_json(out);spatial_json(out,*at<int*>(OFF_CURSOR_X)+*at<int*>(OFF_HOT_X),*at<int*>(OFF_CURSOR_Y)+*at<int*>(OFF_HOT_Y),dude->elevation);
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
    if(target==-8)scan_json(out,elevation);
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
    door_json(out);locker_json(out);spatial_json(out,*at<int*>(OFF_CURSOR_X)+*at<int*>(OFF_HOT_X),*at<int*>(OFF_CURSOR_Y)+*at<int*>(OFF_HOT_Y),dude->elevation);
    std::fprintf(out, ",\"native_Object_bytes\":%zu,\"native_pid_offset\":%zu}\n", sizeof(fallout::Object), offsetof(fallout::Object,pid));
    std::fclose(out);
    return held;
}

