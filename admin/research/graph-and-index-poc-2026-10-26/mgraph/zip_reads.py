# Reading one member out of a zip: Memory-FS's Storage_FS__Zip (as it is) against a ZipFile kept open, and against an
# offset index (one seek + read), on zips of 1,000, 10,000 and 134,092 members.
import io, zipfile, time, os, sys, random, struct, json
from memory_fs.storage_fs.providers.Storage_FS__Zip import Storage_FS__Zip
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
S = os.environ['S']; big = f'{S}/idxexp/by_id.zip'
def small(n):
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w', zipfile.ZIP_STORED) as z:
        for i in range(n): z.writestr(f'bare/data/obj-{i:08d}', os.urandom(400))
    return b.getvalue()
cases = [('1,000 members', small(1000)), ('10,000 members', small(10000)), ('134,092 members (the 76,000-file vault packed)', open(big, 'rb').read())]
out = []
for label, data in cases:
    names = zipfile.ZipFile(io.BytesIO(data)).namelist(); pick = random.Random(1).sample(names, 5)
    fs = Storage_FS__Zip(zip_bytes=data)
    t = time.perf_counter()
    for nme in pick[:3]: assert fs.file__bytes(Safe_Str__File__Path(nme))
    mfs = (time.perf_counter() - t) / 3
    t = time.perf_counter(); zf = zipfile.ZipFile(io.BytesIO(data)); topen = time.perf_counter() - t
    t = time.perf_counter()
    for nme in pick: zf.read(nme)
    zr = (time.perf_counter() - t) / len(pick)
    t = time.perf_counter(); idx = {}
    for zi in zf.infolist(): idx[zi.filename] = (zi.header_offset + 30 + len(zi.filename.encode()) , zi.file_size)
    tidx = time.perf_counter() - t
    mv = memoryview(data); t = time.perf_counter()
    for nme in pick: off, l = idx[nme]; bytes(mv[off:off+l])
    ir = (time.perf_counter() - t) / len(pick)
    r = dict(zip=label, mb=round(len(data)/1e6, 1), memory_fs_read_ms=round(mfs*1e3, 2), zipfile_open_ms=round(topen*1e3, 1), zipfile_read_us=round(zr*1e6, 1),
             offset_index_build_ms=round(tidx*1e3, 1), offset_read_us=round(ir*1e6, 2))
    print(json.dumps(r), flush=True); out.append(r)
json.dump(out, open(f'{S}/mg/zip_reads.json', 'w'))
