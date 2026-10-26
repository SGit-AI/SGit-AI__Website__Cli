from common import *
import heapq
from collections import defaultdict
par = defaultdict(list); ts = {}
for s, p, o in T:
    if p == 'parent': par[s].append(o)
    elif p == 'ts': ts[s] = int(o)
t = time.perf_counter()
gen = {}
for c in sorted(ts, key=ts.get):                      # parents are always older here, so ts order is topological
    gen[c] = 1 + max((gen[p] for p in par[c]), default=0)
tg = time.perf_counter() - t
def paint(a, b):
    """git's paint-down walk: commits reachable from a and/or b, newest generation first, stopping when every
    commit still queued is reachable from both. Returns the flags of every commit it touched."""
    flags = defaultdict(int); flags[a] |= 1; flags[b] |= 2
    q = [(-gen[a], a), (-gen[b], b)]; heapq.heapify(q); seen = {a, b}
    while q and any(flags[c] != 3 for _, c in q):
        _, c = heapq.heappop(q)
        f = flags[c]
        for p in par[c]:
            flags[p] |= f
            if p not in seen: seen.add(p); heapq.heappush(q, (-gen[p], p))
    return flags
def merge_base(a, b):
    f = paint(a, b); common = [c for c, v in f.items() if v == 3]
    return max(common, key=lambda c: gen[c])
def between(base, head):
    f = paint(head, base); return sum(1 for v in f.values() if v == 1)
R = {}
R['merge_base']   = timed(lambda: merge_base(M['head'], M['side_tip']))
R['base_to_head'] = timed(lambda: between(M['base'], M['head']))
print(f'generation numbers for {len(gen)} commits: {tg*1e3:.0f} ms')
truth = json.load(open(f'{GX}/truth.json'))
for q, (v, sec) in R.items(): print(f'  {q:14s} {sec*1e3:.3f} ms  {v}  {"ok" if truth[q]==v else "MISMATCH"}')
with open(f'{GX}/results.jsonl', 'a') as f:
    f.write(json.dumps(dict(engine='python + generation numbers (stdlib)', load_s=round(tg, 3), size_mb=None, extra='',
        q={q: dict(ms=round(s*1e3, 3), val=v, ok='ok' if truth[q]==v else 'MISMATCH') for q, (v, s) in R.items()})) + '\n')
