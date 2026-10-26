import zipfile, os, sys, sqlite3, time, struct, zlib
S=sys.argv[1]; OUT=f'{S}/idxexp'; W=f'{S}/bench/v'
p=f'{OUT}/by_id.zip'; size=os.path.getsize(p)
with open(p,'rb') as f:
    f.seek(-22-20-56, 2); tail=f.read()
with zipfile.ZipFile(p) as z: cd_start = min(zi.header_offset for zi in z.infolist())
# central directory offset from zip64 EOCD or EOCD
import re
with zipfile.ZipFile(p) as z:
    pass
f=open(p,'rb'); data=f.read(); i=data.rfind(b'PK\x05\x06'); cd_size, cd_off = struct.unpack('<II', data[i+12:i+20])
if cd_off == 0xFFFFFFFF or cd_size == 0xFFFFFFFF:
    j=data.rfind(b'PK\x06\x06'); cd_size, cd_off = struct.unpack('<QQ', data[j+40:j+56])
print(f'central directory: {cd_size/1e6:.1f} MB of a {size/1e6:.0f} MB pack ({cd_size/134092:.0f} bytes a member)')
print('fts5:', 'ENABLE_FTS5' in ' '.join(r[0] for r in sqlite3.connect(':memory:').execute('PRAGMA compile_options')))
files=[]
for root,_,fs in os.walk(W):
    if '.sg_vault' in root: continue
    for n in fs:
        if n.endswith(('.md','.json','.txt')): files.append(os.path.join(root,n))
db_path=f'{OUT}/fts.db'
if os.path.exists(db_path): os.remove(db_path)
db=sqlite3.connect(db_path); db.execute('PRAGMA journal_mode=OFF')
db.execute("CREATE VIRTUAL TABLE docs USING fts5(path UNINDEXED, body)")
t=time.perf_counter(); nb=0
for fp in files:
    b=open(fp,encoding='utf-8',errors='replace').read(); nb+=len(b)
    db.execute('INSERT INTO docs VALUES(?,?)',(os.path.relpath(fp,W),b))
db.commit(); db.execute("INSERT INTO docs(docs) VALUES('optimize')"); db.commit(); db.execute('VACUUM'); tb=time.perf_counter()-t
sz=os.path.getsize(db_path); z=len(zlib.compress(open(db_path,'rb').read(),6))
word = db.execute("SELECT body FROM docs LIMIT 1").fetchone()[0].split()[3]
t=time.perf_counter(); r=db.execute('SELECT path FROM docs WHERE docs MATCH ? LIMIT 50',(word,)).fetchall(); tq=time.perf_counter()-t
print(f'full-text index over {len(files)} files ({nb/1e6:.1f} MB of text): built in {tb:.1f} s; {sz/1e6:.1f} MB, deflated {z/1e6:.1f} MB; a query {tq*1e3:.1f} ms ({len(r)} hits)')
