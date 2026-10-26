import json, zlib, time, os, hmac, hashlib, array
from collections import Counter, defaultdict
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
S = os.environ['S']; T = json.load(open(f'{S}/gx/triples.json')); M = json.load(open(f'{S}/gx/meta.json'))
key = AESGCM.generate_key(256); aes = AESGCM(key)
raw = json.dumps(T, separators=(',', ':')).encode(); z = zlib.compress(raw, 6)
print(f'triples as JSON: {len(raw)/1e6:.1f} MB, deflated {len(z)/1e6:.2f} MB')
# dictionary-encoded columns: a term list plus three int32 columns
terms = {}; cols = [array.array('i'), array.array('i'), array.array('i')]
for tr in T:
    for k, x in enumerate(tr):
        if x not in terms: terms[x] = len(terms)
        cols[k].append(terms[x])
enc = json.dumps(list(terms), separators=(',', ':')).encode() + b''.join(c.tobytes() for c in cols)
ze = zlib.compress(enc, 9)
print(f'dictionary-encoded: {len(enc)/1e6:.1f} MB, deflated {len(ze)/1e6:.2f} MB ({len(terms)} distinct terms)')
# one encrypted member for everything
t = time.perf_counter(); nonce = os.urandom(12); ct = aes.encrypt(nonce, z, None); te = time.perf_counter() - t
t = time.perf_counter(); pt = zlib.decompress(aes.decrypt(nonce, ct, None)); T2 = json.loads(pt); td = time.perf_counter() - t
print(f'one member: encrypt {te*1e3:.0f} ms; decrypt + inflate + parse {td*1e3:.0f} ms')
# sharded by push: each commit's own triples (its parents, ts, changed) as one member, as a commit pack would carry
by = defaultdict(list)
for s, p, o in T:
    if p in ('parent', 'ts', 'changed'): by[s].append((s, p, o))
sizes = []; t = time.perf_counter()
for c, rows in by.items():
    b = zlib.compress(json.dumps(rows, separators=(',', ':')).encode(), 6); n = os.urandom(12); sizes.append(len(aes.encrypt(n, b, None)) + 12)
te = time.perf_counter() - t
sizes.sort()
print(f'per-commit shards: {len(sizes)} members, median {sizes[len(sizes)//2]} bytes, total {sum(sizes)/1e6:.1f} MB, encrypt all {te*1e3:.0f} ms')
# keyed pseudonyms: what a host would learn from the structure alone if relations were shipped with HMAC'd ids
hk = os.urandom(32)
t = time.perf_counter(); H = {x: hmac.new(hk, x.encode(), hashlib.sha256).hexdigest()[:16] for x in terms}; th = time.perf_counter() - t
outdeg = Counter(s for s, p, o in T if p == 'contains'); changes = Counter(o for s, p, o in T if p == 'changed')
print(f'HMAC of {len(H)} terms: {th*1e3:.0f} ms')
print(f'what the shape alone tells a host: {len(outdeg)} folders; the largest has {outdeg.most_common(1)[0][1]} children; '
      f'files changed most often: {changes.most_common(1)[0][1]} times; commits per day are visible from the ts edges')
