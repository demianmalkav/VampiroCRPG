// Private lab compilation reads pinned CE's native type layouts only.
// Section garbage collection discards the included engine implementation.
#include "animation.cc"
#include <cstddef>
int main(){using namespace fallout;
std::printf("{\"sequence_size\":%zu,\"description_size\":%zu,\"sequence_descriptions\":%zu,\"kind\":%zu,\"owner\":%zu,\"destination\":%zu,\"anim\":%zu,\"delay\":%zu,\"callback\":%zu,\"forced_flags\":%zu}\n",sizeof(AnimationSequence),sizeof(AnimationDescription),offsetof(AnimationSequence,animations),offsetof(AnimationDescription,kind),offsetof(AnimationDescription,owner),offsetof(AnimationDescription,destination),offsetof(AnimationDescription,anim),offsetof(AnimationDescription,delay),offsetof(AnimationDescription,callback),offsetof(AnimationDescription,extendedFlags));}
