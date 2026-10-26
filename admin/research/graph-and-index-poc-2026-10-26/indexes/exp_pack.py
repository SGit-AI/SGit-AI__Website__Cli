import json, zipfile, time, os, sys, random, shutil, struct
S = sys.argv[1]; V = f'{S}/bench/v/.sg_vault/bare/data'; OUT = f'{S}/idxexp'
head = json.load(open(f'{S}/bench/v/.sg_vault/local/flat-cache/obj-cas-imm-7473af178535.json'))
ids = sorted(os.listdir(V))
def write(path, order):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_STORED, allowZip64=True) as z:
        for oid in order:
            zi = zipfile.ZipInfo(f'bare/data/{oid}', (1980,1,1,0,0,0)); zi.compress_type = zipfile.ZIP_STORED
            z.writestr(zi, open(f'{V}/{oid}','rb').read())
t=time.perf_counter(); write(f'{OUT}/by_id.zip', ids); print(f'pack of {len(ids)} objects by id: {time.perf_counter()-t:.1f} s, {os.path.getsize(OUT+"/by_id.zip")/1e6:.0f} MB')
# path order: trees and commits first (by id), then blobs in path order
blob_of = {p: e['blob_id'] for p, e in head['flat'].items()}
blobs_in_path = []; seen=set()
for p in sorted(blob_of):
    b = blob_of[p]
    if b not in seen: seen.add(b); blobs_in_path.append(b)
rest = [i for i in ids if i not in seen]
order = rest + blobs_in_path
write(f'{OUT}/by_path.zip', order)
# index the central directory: id -> (offset of data, length)
def index(path):
    t=time.perf_counter(); idx={}
    with zipfile.ZipFile(path) as z, open(path,'rb') as f:
        for zi in z.infolist():
            f.seek(zi.header_offset); h=f.read(30); n,e=struct.unpack('<HH',h[26:30])
            idx[zi.filename[10:]] = (zi.header_offset+30+n+e, zi.file_size)
    return idx, time.perf_counter()-t
idx, ti = index(f'{OUT}/by_id.zip'); print(f'pack index from the central directory (with local headers): {ti:.2f} s for {len(idx)} members')
t=time.perf_counter()
with zipfile.ZipFile(f'{OUT}/by_id.zip') as z: n=len(z.infolist())
print(f'  central directory alone: {time.perf_counter()-t:.2f} s')
# random reads in place
f=open(f'{OUT}/by_id.zip','rb'); sample=random.Random(1).sample(ids, 2000)
t=time.perf_counter()
for oid in sample:
    off,l=idx[oid]; f.seek(off); assert len(f.read(l))==l
print(f'read in place: {(time.perf_counter()-t)/2000*1e6:.0f} us per object (warm page cache)')
# extract all loose
dst=f'{OUT}/loose'; shutil.rmtree(dst, ignore_errors=True); os.makedirs(dst)
t=time.perf_counter()
with zipfile.ZipFile(f'{OUT}/by_id.zip') as z:
    for zi in z.infolist():
        with open(f'{dst}/{zi.filename[10:]}','wb') as o: o.write(z.read(zi))
print(f'extract every object loose (today): {time.perf_counter()-t:.1f} s')
shutil.rmtree(dst)
# scoped fetch: blobs under a folder, as HTTP ranges, coalescing gaps under 64 KB
def ranges(path, want, gap=64*1024):
    ix,_ = index(path); spans = sorted(ix[w] for w in want); out=[]
    for off,l in spans:
        if out and off - (out[-1][0]+out[-1][1]) <= gap: out[-1][1] = off+l-out[-1][0]
        else: out.append([off,l])
    return len(out), sum(l for _,l in out)
for folder in ['raw/c09/', 'raw/c09/s4/', 'raw/c09/s4/pub19/']:
    want = {b for p,b in blob_of.items() if p.startswith(folder)}
    a = ranges(f'{OUT}/by_id.zip', want); b = ranges(f'{OUT}/by_path.zip', want)
    print(f'scope {folder}: {len(want)} blobs; ranges by id {a[0]} ({a[1]/1e6:.1f} MB), by path {b[0]} ({b[1]/1e6:.2f} MB)')
