from common import *
from collections import defaultdict
t = time.perf_counter()
out = defaultdict(lambda: defaultdict(list)); inc = defaultdict(lambda: defaultdict(list))
for s, p, o in T: out[p][s].append(o); inc[p][o].append(s)
load = time.perf_counter() - t
def ancestors(c):
    seen = set(); st = [c]
    while st:
        x = st.pop()
        for y in out['parent'].get(x, ()):
            if y not in seen: seen.add(y); st.append(y)
    return seen
def subtree(d):
    n = 0; st = [d]
    while st:
        x = st.pop()
        for y in out['contains'].get(x, ()):
            if y.startswith('f:'): n += 1
            else: st.append(y)
    return n
def to_root(f):
    path = []; x = f
    while x in inc['contains']: x = inc['contains'][x][0]; path.append(x)
    return len(path)
def merge_base(a, b):
    A = ancestors(a) | {a}; B = ancestors(b) | {b}; common = A & B
    best = [c for c in common if not any(c in ancestors(o) for o in [])]
    # the best common ancestors: those not an ancestor of another common ancestor; on this DAG the newest by ts
    ts = {c: int(out['ts'][c][0]) for c in common}
    return max(common, key=ts.get)
R = {}
R['children']          = timed(lambda: len(out['contains'][f'd:{M["folder_deep"]}']))
R['subtree_files']     = timed(lambda: subtree(f'd:{M["folder"]}'))
R['file_to_root']      = timed(lambda: to_root(f'f:{M["file"]}'))
R['ancestors_of_head'] = timed(lambda: len(ancestors(M['head'])))
R['merge_base']        = timed(lambda: merge_base(M['head'], M['side_tip']))
R['base_to_head']      = timed(lambda: len((ancestors(M['head']) | {M['head']}) - (ancestors(M['base']) | {M['base']})))
R['file_history']      = timed(lambda: len(inc['changed'].get(f'f:{M["file"]}', [])))
R['paths_of_blob']     = timed(lambda: len(inc['blob'].get(M['blob'], [])))
json.dump({q: v for q, (v, _) in R.items()}, open(f'{GX}/truth.json', 'w'))
report('python dicts (stdlib)', load, None, R)
