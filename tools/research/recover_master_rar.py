"""Private staging utility: stream a single named input from a split archive."""
import ctypes as c
import ctypes.util
import hashlib
import json
from pathlib import Path
import sys

lib = c.CDLL(ctypes.util.find_library('archive'))
def fn(name, args, result):
    f = getattr(lib, name); f.argtypes = args; f.restype = result; return f
ptr = c.c_void_p
new = fn('archive_read_new', [], ptr)
all_filters = fn('archive_read_support_filter_all', [ptr], c.c_int)
all_formats = fn('archive_read_support_format_all', [ptr], c.c_int)
open_files = fn('archive_read_open_filenames', [ptr, c.POINTER(c.c_char_p), c.c_size_t], c.c_int)
next_header = fn('archive_read_next_header', [ptr, c.POINTER(ptr)], c.c_int)
pathname = fn('archive_entry_pathname', [ptr], c.c_char_p)
entry_size = fn('archive_entry_size', [ptr], c.c_int64)
read_data = fn('archive_read_data', [ptr, ptr, c.c_size_t], c.c_ssize_t)
error = fn('archive_error_string', [ptr], c.c_char_p)
free = fn('archive_read_free', [ptr], c.c_int)
version = fn('archive_version_string', [], c.c_char_p)
format_name = fn('archive_format_name', [ptr], c.c_char_p)

out = Path(sys.argv[1]); expected = int(sys.argv[2]); parts = [Path(x) for x in sys.argv[3:]]
if out.exists():
    raise FileExistsError("Reference output already exists; refusing to overwrite")
filenames = (c.c_char_p * (len(parts) + 1))(*[str(p).encode() for p in parts], None)
a = new(); temp = out.with_suffix('.partial')
def checked(result):
    if result < 0:
        raise RuntimeError((error(a) or b'archive failure').decode(errors='replace'))
    return result
try:
    checked(all_filters(a)); checked(all_formats(a)); checked(open_files(a, filenames, 65536))
    entry = ptr(); checked(next_header(a, c.byref(entry)))
    name = pathname(entry).decode()
    size = entry_size(entry)
    print(json.dumps({'entry':name,'size':size,'libarchive':version().decode(),'format':format_name(a).decode()}),flush=True)
    if name.replace('\\','/').split('/')[-1].lower() != 'master.dat' or size != expected:
        raise ValueError('Unexpected entry or size')
    buf = c.create_string_buffer(1024 * 1024); count = 0; sha = hashlib.sha256(); md5 = hashlib.md5()
    with temp.open('xb') as f:
        while True:
            n = checked(read_data(a,buf,len(buf)))
            if n == 0: break
            count += n
            if count > expected: raise ValueError('Output exceeds expected size')
            data = buf.raw[:n]; f.write(data); sha.update(data); md5.update(data)
    if count != expected: raise ValueError('Output incomplete')
    result = next_header(a,c.byref(entry))
    if result != 1:
        checked(result); raise ValueError('Unexpected additional entry')
    temp.rename(out)
    print(json.dumps({'output':out.name,'bytes':count,'sha256':sha.hexdigest(),'md5':md5.hexdigest(),'archive_end':'EOF'}))
finally:
    free(a)
