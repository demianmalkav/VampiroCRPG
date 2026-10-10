// Private laboratory input adapter; no game implementation or assets included.
// Compiled against clean CE headers and offsets extracted from the exact ELF.
// Only substitutes SDL relative mouse input. Native query calls are read-only.
#include <SDL.h>
#include <dlfcn.h>
#include <link.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
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
    std::fprintf(out, "{\"id\":%d,\"tile\":%d,\"pid\":%u,\"fid\":%u,\"flags\":%u,\"frame\":%d,\"rotation\":%d,\"elevation\":%d,\"x\":%d,\"y\":%d,\"data_flags\":%d,\"inventory_length\":%d}",
        obj->id, obj->tile, unsigned(obj->pid), unsigned(obj->fid), unsigned(obj->flags),
        obj->frame, obj->rotation, obj->elevation, obj->x, obj->y, obj->data.flags, obj->data.inventory.length);
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
    if (!door) {std::fputs(",\"selected_object\":",out);object_json(out,at<fallout::Object* (*)(int,bool,int)>(OFF_SELECT)(-1,true,*at<int*>(OFF_ELEVATION)));return;}
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


// This pointer is laboratory observation state only, never a gameplay write.
static fallout::Object* watched_item=nullptr;
static bool on_map(const fallout::Object* obj) {
    if(!obj || obj->tile<0 || obj->tile>=40000)return false;
    for(auto n=at<fallout::ObjectListNode**>(OFF_OBJECT_TABLE)[obj->tile];n;n=n->next)
        if(n->obj==obj)return true;
    return false;
}
static void watch_json(FILE* out) {
    auto dude=*at<fallout::Object**>(OFF_DUDE);
    std::fputs(",\"actor_inventory\":",out);inventory_json(out,dude);
    std::fputs(",\"watched_item\":",out);object_json(out,watched_item);
    std::fputs(",\"watched_owner\":",out);object_json(out,watched_item?watched_item->owner:nullptr);
    std::fprintf(out,",\"inventory_visible\":%s",inventory_visible()?"true":"false");
    std::fprintf(out,",\"watched_on_map\":%s,\"inventory_cursor\":%d",on_map(watched_item)?"true":"false",*at<int*>(OFF_INV_CURSOR));
    if(inventory_visible()) {
        fallout::Rect rect;at<void (*)(int,fallout::Rect*)>(OFF_WINDOW_RECT)(*at<int*>(OFF_INV_WINDOW),&rect);
        std::fprintf(out,",\"inventory_rect\":[%d,%d,%d,%d],\"inventory_scroll\":%d",rect.left,rect.top,rect.right,rect.bottom,*at<int*>(OFF_INV_SCROLL));
    }
    int start=*at<int*>(OFF_MONITOR_START),cap=*at<int*>(OFF_MONITOR_CAP);
    std::fprintf(out,",\"monitor_start\":%d,\"monitor_recent_hex\":[",start);
    if(cap>0 && cap<=100)for(int j=2;j>0;j--){auto line=at<unsigned char*>(OFF_MONITOR_LINES)+((start+cap-j)%cap)*80;if(j!=2)std::fputc(',',out);std::fputc('"',out);for(int k=0;k<80 && line[k];k++)std::fprintf(out,"%02x",line[k]);std::fputc('"',out);}std::fputc(']',out);
    if(!watched_item)return;
    fallout::Rect rect;at<void (*)(fallout::Object*,fallout::Rect*)>(OFF_RECT)(watched_item,&rect);
    int item_type=at<int (*)(fallout::Object*)>(OFF_ITEM_TYPE)(watched_item);
    int drop_index=(item_type==3 && at<bool (*)(fallout::Object*)>(OFF_CAN_UNLOAD)(watched_item)) || at<bool (*)(fallout::Object*)>(OFF_CAN_USE)(watched_item) || at<bool (*)(int)>(OFF_CAN_USE_ON)(watched_item->pid)?2:1;
    std::fprintf(out,",\"watched_rect\":[%d,%d,%d,%d],\"watched_portable\":%s,\"watched_type\":%d,\"watched_drop_index\":%d,\"watched_distance\":%d",rect.left,rect.top,rect.right,rect.bottom,at<int (*)(int)>(OFF_CAN_PICKUP)(watched_item->pid)?"true":"false",item_type,drop_index,watched_item->owner?-1:at<int (*)(fallout::Object*,fallout::Object*)>(OFF_DISTANCE)(dude,watched_item));
}

// Layout constants are generated by the compiler against the exact pinned source.
// Query only sequence fields; no queue/callback/function is invoked or changed.
template<class T> static T field(const unsigned char* p, size_t offset) {
    T value; std::memcpy(&value,p+offset,sizeof(T)); return value;
}
static void queue_json(FILE* out) {
    auto dude=*at<fallout::Object**>(OFF_DUDE);
    auto bytes=at<unsigned char*>(OFF_SEQUENCES);
    std::fputs(",\"actor_sequences\":[",out);bool comma=false;
    for(int i=0;i<32;i++) {
        auto seq=bytes+i*LAY_SEQUENCE_SIZE;
        int cursor=field<int>(seq,0),completed=field<int>(seq,4),length=field<int>(seq,8);
        if(cursor==-1000 || length<0 || length>55)continue;
        bool belongs=false;
        for(int j=0;j<length;j++) {
            auto ad=seq+LAY_SEQUENCE_DESCRIPTIONS+j*LAY_DESCRIPTION_SIZE;
            int kind=field<int>(ad,LAY_KIND);
            auto owner=field<void*>(ad,LAY_OWNER),dest=field<void*>(ad,LAY_DESTINATION);
            if(owner==dude || ((kind==11 || kind==0) && dest==dude))belongs=true;
        }
        if(!belongs)continue;
        if(comma)std::fputc(',',out);comma=true;
        std::fprintf(out,"{\"slot\":%d,\"cursor\":%d,\"completed\":%d,\"length\":%d,\"flags\":%u,\"descriptions\":[",i,cursor,completed,length,field<unsigned>(seq,12));
        for(int j=0;j<length;j++) {
            auto ad=seq+LAY_SEQUENCE_DESCRIPTIONS+j*LAY_DESCRIPTION_SIZE;
            int kind=field<int>(ad,LAY_KIND);
            auto cb=field<uintptr_t>(ad,LAY_CALLBACK);
            const char* name=kind!=11?"none":cb==base+OFF_PICKUP?"pickup":cb==base+OFF_NEXT_TO?"next_to":cb==base+OFF_AP_COST?"ap_cost":"other";
            std::fprintf(out,"%s{\"index\":%d,\"kind\":%d,\"anim\":%d,\"delay\":%d,\"callback\":\"%s\",\"actor_owner\":%s,\"actor_param1\":%s,\"target_param2\":%s,\"forced\":%u}",j?",":"",j,kind,field<int>(ad,LAY_ANIM),field<int>(ad,LAY_DELAY),name,field<void*>(ad,LAY_OWNER)==dude?"true":"false",field<void*>(ad,LAY_DESTINATION)==dude?"true":"false",field<void*>(ad,LAY_OWNER)==watched_item?"true":"false",kind==11?field<unsigned>(ad,LAY_FORCED_FLAGS):0);
        }
        std::fputs("]}",out);
    }
    std::fputc(']',out);
}

static void record_tile_transition(long sequence) {
    const char* path = std::getenv("CE_PROBE_MOTION");
    if (!path) return;
    static int last_locker_frame=-1,last_inventory=-1,last_monitor=-1,last_watch_tile=-999,last_inventory_length=-1;
    static const fallout::Object* last_watch_owner=nullptr;
    static int last_tile = -1, last_frame=-1, last_fid=-1, last_x=-999, last_y=-999, door_frame=-1, door_flags=-1, door_open=-1;
    auto dude = *at<fallout::Object**>(OFF_DUDE);
    if (!dude || dude->tile < 0) return;
    auto door=reference_door();
    auto locker=reference_locker();
    int lf=locker?locker->frame:-1,iv=inventory_visible(),ms=*at<int*>(OFF_MONITOR_START);
    int wt=watched_item?watched_item->tile:-999;auto wo=watched_item?watched_item->owner:nullptr;int il=dude->data.inventory.length;
    static std::string last_queue;char* queue_buffer=nullptr;size_t queue_bytes=0;FILE* queue_stream=open_memstream(&queue_buffer,&queue_bytes);queue_json(queue_stream);std::fclose(queue_stream);std::string current_queue(queue_buffer,queue_bytes);std::free(queue_buffer);
    if (current_queue==last_queue && wt==last_watch_tile && wo==last_watch_owner && il==last_inventory_length && lf==last_locker_frame && iv==last_inventory && ms==last_monitor && dude->tile==last_tile && dude->frame==last_frame && dude->fid==last_fid && dude->x==last_x && dude->y==last_y && (door?door->frame:-1)==door_frame && (door?int(door->flags):-1)==door_flags && (door?door->data.scenery.door.openFlags:-1)==door_open) return;
    last_queue=current_queue;
    last_watch_tile=wt;last_watch_owner=wo;last_inventory_length=il;
    last_locker_frame=lf;last_inventory=iv;last_monitor=ms;
    last_frame=dude->frame;last_fid=dude->fid;last_x=dude->x;last_y=dude->y;
    door_frame=(door?door->frame:-1);door_flags=(door?int(door->flags):-1);door_open=(door?door->data.scenery.door.openFlags:-1);
    last_tile = dude->tile;
    auto blocking = at<fallout::Object* (*)(fallout::Object*, int, int)>(OFF_BLOCKING);
    FILE* out = std::fopen(path, "a");
    if (!out) return;
    std::fprintf(out, "{\"sdl_tick_ms\":%u,\"input_sequence\":%ld,\"dude\":", SDL_GetTicks(), sequence);
    object_json(out, dude);
    std::fputs(",\"blocker_at_actor\":", out);
    object_json(out, blocking(dude, dude->tile, dude->elevation));
    door_json(out);watch_json(out);queue_json(out);
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
    if(target==-6)watched_item=nullptr;
    if(target==-7){watched_item=reference_locker();for(int i=0;i<dude->data.inventory.length;i++)if(dude->data.inventory.items[i].item->pid==unsigned(std::atoi(std::getenv("CE_CONTAINER_PID"))) && dude->data.inventory.items[i].quantity==1)watched_item=dude->data.inventory.items[i].item;}
    if(target==-5)watched_item=reference_locker();
    if(target==-4 && count==5 && input_x>=0 && input_x<dude->data.inventory.length && dude->data.inventory.items[input_x].quantity==1)watched_item=dude->data.inventory.items[input_x].item;
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
    door_json(out);watch_json(out);queue_json(out);
    std::fprintf(out, ",\"native_Object_bytes\":%zu,\"native_pid_offset\":%zu}\n", sizeof(fallout::Object), offsetof(fallout::Object,pid));
    std::fclose(out);
    return held;
}
