# End-to-end checks of one installed sgit-ai build, on its in-memory host. Each check runs only on the builds
# that claim the behaviour; earlier builds show it as "n/a" (or as the old behaviour, where that is the point).
#   python -I check_build.py [OUT.json]      with the Python of the build under test; needs git on PATH
import os, sys, io, re, json, time, random, shutil, subprocess, tempfile, traceback
import sgit_ai
from sgit_ai.core.Vault__Sync                  import Vault__Sync
from sgit_ai.crypto.Vault__Crypto              import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory

VERSION = open(os.path.join(os.path.dirname(sgit_ai.__file__), 'version')).read().strip()
V = tuple(int(x) for x in re.match(r'v?(\d+)\.(\d+)\.(\d+)', VERSION).groups())
GIT = shutil.which('git')
api = Vault__API__In_Memory().setup()
S = lambda: Vault__Sync(crypto=Vault__Crypto(), api=api)
ROOT = tempfile.mkdtemp(prefix='chk-')
results = []
n = [0]

def d(name):
    n[0] += 1; return os.path.join(ROOT, f'{n[0]:03d}-{name}')
def put(base, rel, text):
    p = os.path.join(base, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb' if isinstance(text, bytes) else 'w').write(text)
def get(base, rel):
    return open(os.path.join(base, rel)).read()
def vault(files, packs=False):
    s = S(); a = d('a'); r = s.init(a, packs=packs) if packs else s.init(a)
    key = r.get('vault_key') or open(os.path.join(a, '.sg_vault/local/vault_key')).read().strip()
    for k, v in files.items(): put(a, k, v)
    s.commit(a, message='first'); s.push(a)
    return s, a, key
def objects(directory):
    return sum(len(f) for _, _, f in os.walk(os.path.join(directory, '.sg_vault', 'bare')))

def check(cid, since, title):
    def wrap(fn):
        t0 = time.time()
        if V < since:
            results.append((cid, title, 'n/a', f'claimed from {".".join(map(str, since))}', 0.0)); return fn
        try:
            ok, detail = fn()
            results.append((cid, title, 'PASS' if ok else 'FAIL', detail, time.time() - t0))
        except Exception as e:
            results.append((cid, title, 'ERROR', f'{type(e).__name__}: {str(e)[:160]}', time.time() - t0))
            traceback.print_exc(file=sys.stderr)
        return fn
    return wrap

# ── every build ──────────────────────────────────────────────────────────────────────────────────────────────
@check('P1', (0, 0, 0), 'one push of 150 commits: the host holds all of them')
def _():
    s, a, key = vault({'x.txt': '0\n'})
    for i in range(150):
        put(a, 'x.txt', f'{i + 1}\n'); s.commit(a, message=f'c{i}')
    s.push(a)
    c = d('c'); s.clone(key, c)
    f = s.fsck(c)
    return bool(f.get('ok')), f"fsck of a fresh clone: ok={f.get('ok')}, missing={len(f['missing']) if isinstance(f.get('missing'), list) else f.get('missing')}"

# ── 0.26.1 ───────────────────────────────────────────────────────────────────────────────────────────────────
@check('G1', (0, 26, 1), 'a new pack vault is gated at what its features need (0.24.0)')
def _():
    from sgit_ai.storage.Vault__Format import Vault__Format
    s, a, _ = vault({'x.txt': 'x\n'}, packs=True)
    c = s._init_components(a); idx = c.branch_manager.load_branch_index(a, c.branch_index_file_id, c.read_key)
    mc = Vault__Format().min_client_of(idx)
    return str(mc).lstrip('v') == '0.24.0', f'min_client = {mc}'

@check('G2', (0, 26, 1), '`pack index verify`: all packs, then --last 1')
def _():
    from sgit_ai.core.actions.pack.Vault__Pack_Index import Vault__Pack_Index
    s, a, _ = vault({f'raw/f{i:03d}/n{j}.txt': f'{i} {j}\n' for i in range(150) for j in range(4)}, packs=True)
    for k in range(4):
        put(a, f'raw/f{k:03d}/n0.txt', f'edit {k}\n'); s.commit(a, message=f'e{k}'); s.push(a)
    pi = Vault__Pack_Index(crypto=Vault__Crypto(), api=api)
    t0 = time.time(); full = pi.verify_indexes(a); t_full = time.time() - t0
    t0 = time.time(); last = pi.verify_indexes(a, last=1); t_last = time.time() - t0
    ok = full.get('ok') and last.get('ok')
    return bool(ok), f"600 files, 5 packs: all {t_full:.2f} s (ok={full.get('ok')}), --last 1 {t_last:.2f} s (ok={last.get('ok')})"

# ── 0.26.3 ───────────────────────────────────────────────────────────────────────────────────────────────────
def conflict_pair():
    s, a, key = vault({'doc.txt': 'one\n', 'other.txt': 'o\n'})
    b = d('b'); s.clone(key, b)
    put(a, 'doc.txt', 'from a\n'); s.commit(a, message='a'); s.push(a)
    put(b, 'doc.txt', 'from b\n'); s.commit(b, message='b')
    r = s.pull(b)
    return s, a, b, r

@check('M1', (0, 26, 3), 'commit during an unresolved merge is refused; .conflict never committed')
def _():
    s, a, b, r = conflict_pair()
    try:
        s.commit(b, message='oops'); return False, 'commit went through'
    except Exception as e:
        return 'conflict' in str(e).lower(), f'refused: {type(e).__name__}: {str(e)[:90]}'

@check('M2', (0, 26, 3), '`status` shows the merge in progress')
def _():
    s, a, b, r = conflict_pair()
    st = s.status(b); text = json.dumps(st, default=str)
    return ('merge' in text.lower() and 'doc.txt' in text), f'status keys: {sorted(k for k in st if "merg" in k.lower() or "conflict" in k.lower())}'

@check('M3', (0, 26, 3), 'the same bytes written on both sides is not a conflict')
def _():
    s, a, key = vault({'doc.txt': 'one\n'})
    b = d('b'); s.clone(key, b)
    put(a, 'doc.txt', 'same\n'); s.commit(a, message='a'); s.push(a)
    put(b, 'doc.txt', 'same\n'); put(b, 'b.txt', 'b\n'); s.commit(b, message='b')
    s.pull(b)
    conf = [f for f in os.listdir(b) if f.endswith('.conflict')]
    return not conf, f'conflict files: {conf or "none"}'

@check('M4', (0, 26, 3), 'a fork 250 commits deep each side (pushed 50 at a time) merges cleanly')
def _():
    s, a, key = vault({'shared.txt': 'base\n', 'a/x.txt': '0\n', 'b/y.txt': '0\n'})
    b = d('b'); s.clone(key, b)
    for i in range(250):
        put(a, 'a/x.txt', f'{i + 1}\n'); s.commit(a, message=f'a{i}')
        put(b, 'b/y.txt', f'{i + 1}\n'); s.commit(b, message=f'b{i}')
        if i % 50 == 49: s.push(a)                         # pushes of 50: P1 is a separate finding
    t0 = time.time(); s.pull(b); dt = time.time() - t0
    conf = [os.path.join(r, f) for r, _, fs in os.walk(b) for f in fs if f.endswith('.conflict')]
    ok = not conf and get(b, 'a/x.txt') == '250\n' and get(b, 'b/y.txt') == '250\n'
    return ok, f'pull {dt:.1f} s; conflicts: {len(conf)}; a/x.txt={get(b, "a/x.txt").strip()} b/y.txt={get(b, "b/y.txt").strip()}'

@check('M5', (0, 26, 3), 'a nested vault inside the working copy is never committed')
def _():
    s, a, key = vault({'top.txt': 't\n'})
    inner = os.path.join(a, 'nested'); s.clone(key, inner)
    put(a, 'top.txt', 't2\n'); s.commit(a, message='with nested'); s.push(a)
    c = d('c'); s.clone(key, c)
    leaked = os.path.exists(os.path.join(c, 'nested'))
    return not leaked, 'nested/ in a fresh clone: ' + ('yes (leaked)' if leaked else 'no')

# ── 0.26.4 ───────────────────────────────────────────────────────────────────────────────────────────────────
@check('L1', (0, 26, 4), 'a 741-byte message is refused before anything is written')
def _():
    s, a, _ = vault({'x.txt': 'x\n'})
    put(a, 'x.txt', 'x2\n'); before = objects(a)
    try:
        s.commit(a, message='m' * 741); return False, 'accepted on a vault without long-messages'
    except Exception as e:
        return objects(a) == before, f'{type(e).__name__}: {str(e)[:80]}; objects {before} → {objects(a)}'

@check('L2', (0, 26, 4), 'long-messages: 64 KiB accepted, read back by a fresh clone; gate 0.26.4')
def _():
    from sgit_ai.storage.Vault__Format import Vault__Format
    s, a, key = vault({'x.txt': 'x\n'})
    s.set_format(a, add_features=['long-messages'])
    msg = ('é' * 100) + 'm' * (65536 - 200)
    put(a, 'x.txt', 'x2\n'); s.commit(a, message=msg); s.push(a)
    c = d('c'); s.clone(key, c)
    idx_c = s._init_components(a); idx = idx_c.branch_manager.load_branch_index(a, idx_c.branch_index_file_id, idx_c.read_key)
    mc = Vault__Format().min_client_of(idx)
    over = 'm' * 65537
    put(a, 'x.txt', 'x3\n')
    try: s.commit(a, message=over); over_r = 'accepted'
    except Exception as e: over_r = 'refused'
    return (str(mc).lstrip('v') == '0.26.4' and over_r == 'refused'), f'{len(msg.encode())} B ok; clone ok; min_client {mc}; 64 KiB+1 {over_r}'

# ── 0.26.5 ───────────────────────────────────────────────────────────────────────────────────────────────────
TEXT = ''.join(f'line {i}\n' for i in range(1, 21))
def two_clones(text=TEXT):
    s, a, key = vault({'notes.txt': text})
    b = d('b'); s.clone(key, b); return s, a, b

@check('X1', (0, 26, 5), '`pull --merge lines`: edits to different lines merge cleanly')
def _():
    s, a, b = two_clones()
    put(a, 'notes.txt', TEXT.replace('line 2\n', 'line 2 by a\n')); s.commit(a, message='a'); s.push(a)
    put(b, 'notes.txt', TEXT.replace('line 18\n', 'line 18 by b\n')); s.commit(b, message='b')
    s.pull(b, merge_style='lines')
    got = get(b, 'notes.txt'); conf = os.path.exists(os.path.join(b, 'notes.txt.conflict'))
    return ('line 2 by a' in got and 'line 18 by b' in got and '<<<<<<<' not in got and not conf), 'both edits in the file; no markers; no .conflict'

@check('X2', (0, 26, 5), 'same line on both sides: markers; commit refuses until they are gone')
def _():
    s, a, b = two_clones()
    put(a, 'notes.txt', TEXT.replace('line 5\n', 'line 5 by a\n')); s.commit(a, message='a'); s.push(a)
    put(b, 'notes.txt', TEXT.replace('line 5\n', 'line 5 by b\n')); s.commit(b, message='b')
    s.pull(b, merge_style='lines'); got = get(b, 'notes.txt')
    markers = got.count('<<<<<<<') == 1 and '=======' in got and '>>>>>>>' in got
    try: s.commit(b, message='with markers'); refused = False
    except Exception: refused = True
    return markers and refused, f'markers: {markers}; commit with markers refused: {refused}'

@check('X3', (0, 26, 5), 'the default is unchanged: whole-file .conflict')
def _():
    s, a, b = two_clones()
    put(a, 'notes.txt', TEXT.replace('line 2\n', 'line 2 by a\n')); s.commit(a, message='a'); s.push(a)
    put(b, 'notes.txt', TEXT.replace('line 18\n', 'line 18 by b\n')); s.commit(b, message='b')
    s.pull(b)
    conf = os.path.exists(os.path.join(b, 'notes.txt.conflict'))
    return conf and '<<<<<<<' not in get(b, 'notes.txt'), f'notes.txt.conflict written: {conf}'

@check('X4', (0, 26, 5), 'an uncommitted edit to a file that would get markers refuses the pull')
def _():
    s, a, b = two_clones()
    put(a, 'notes.txt', TEXT.replace('line 5\n', 'line 5 by a\n')); s.commit(a, message='a'); s.push(a)
    put(b, 'notes.txt', TEXT.replace('line 5\n', 'line 5 by b\n')); s.commit(b, message='b')
    put(b, 'notes.txt', TEXT.replace('line 5\n', 'line 5 by b, then edited\n'))
    try: s.pull(b, merge_style='lines'); refused = False
    except Exception as e: refused = True
    kept = 'then edited' in get(b, 'notes.txt')
    return refused and kept, f'refused: {refused}; the edit kept: {kept}'

# ── 0.26.6 ───────────────────────────────────────────────────────────────────────────────────────────────────
def committed(s, directory):
    from sgit_ai.core.Vault__Head_Paths import Vault__Head_Paths
    flat = Vault__Head_Paths(crypto=s.crypto).flat(directory)
    return {p: s.sparse_cat(directory, p).decode() for p in sorted(flat)}
def git(repo, *args, inp=None):
    return subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True, input=inp, check=True).stdout
def git_repo(files):
    g = d('git'); os.makedirs(g); git(g, 'init', '-q'); git(g, 'config', 'user.email', 'a@b'); git(g, 'config', 'user.name', 'a')
    git(g, 'config', 'core.autocrlf', 'false')
    for k, v in files.items(): put(g, k, v)
    git(g, 'add', '-A'); git(g, 'commit', '-qm', 'first'); return g
def git_tree(g):
    out = {}
    for p in git(g, 'ls-files').splitlines(): out[p] = git(g, 'show', f'HEAD:{p}')
    return out

@check('C1', (0, 26, 6), '`commit <paths>` against `git add -A -- <paths>; git commit`, 40 random cases')
def _():
    rnd = random.Random(7); bad = []
    for case in range(40):
        files = {f'{fo}/{n}.{ext}': f'{fo} {n}\n' for fo in ('docs', 'src', 'src/deep', 'other') for n in 'abc' for ext in ('md', 'py')}
        files['top.txt'] = 'top\n'
        s, a, _ = vault(files); g = git_repo(files)
        for _ in range(rnd.randint(2, 6)):
            op = rnd.random(); p = rnd.choice(sorted(files))
            if op < .5:   [put(x, p, f'changed {case}\n') for x in (a, g)]
            elif op < .7: [os.remove(os.path.join(x, p)) for x in (a, g) if os.path.exists(os.path.join(x, p))]
            else:
                np = rnd.choice(['docs', 'src/deep', 'new']) + f'/n{rnd.randint(0, 9)}.md'; [put(x, np, 'new\n') for x in (a, g)]
        changed = git(g, 'status', '--porcelain', '-uall').splitlines()
        if not changed: continue
        cands = sorted({l[3:].split('/')[0] for l in changed}) + ['*.md', 'src/deep'] + [l[3:] for l in changed]
        spec = rnd.sample(cands, rnd.randint(1, 2))
        matched = git(g, 'status', '--porcelain', '-uall', '--', *spec).strip()
        try:
            r = s.commit(a, message='x', paths=spec); sg = 'ok'
        except Exception as e:
            sg = type(e).__name__
        if not matched:
            if sg == 'ok': bad.append((case, spec, 'sgit committed, git matched nothing'))
            continue
        git(g, 'add', '-A', '--', *spec); git(g, 'commit', '-qm', 'x')
        if sg != 'ok': bad.append((case, spec, f'sgit refused: {sg}')); continue
        if committed(s, a) != git_tree(g): bad.append((case, spec, 'trees differ'))
    return not bad, f'40 cases; differences: {bad[:3] or "none"}'

def hunk_case(rnd, case):
    base = [f'def f{i}():\n    return {i}\n' if rnd.random() < .7 else '\n' for i in range(rnd.randint(8, 40))]
    work = list(base)
    for _ in range(rnd.randint(1, 5)):
        i = rnd.randrange(len(work) + 1); op = rnd.random()
        if op < .4 and work: del work[min(i, len(work) - 1)]
        elif op < .8:        work.insert(i, f'# added {case} {rnd.randint(0, 999)}\n')
        elif work:           work[min(i, len(work) - 1)] = f'changed {case}\n'
    return ''.join(base), ''.join(work)

@check('C2', (0, 26, 6), 'hunk commits against `git apply --cached`, headers against `git diff -U3`, 60 cases')
def _():
    rnd = random.Random(11); bad = []; total = 0
    for case in range(60):
        base, work = hunk_case(rnd, case)
        if base == work: continue
        s, a, _ = vault({'m.py': base}); g = git_repo({'m.py': base})
        put(a, 'm.py', work); put(g, 'm.py', work)
        listing = s.list_hunks(a, paths=['m.py'])
        hunks = [h for f in listing.files for h in f.hunks]
        diff = git(g, 'diff', '-U3', '--', 'm.py')
        head, *ghunks = re.split(r'(?m)^(?=@@ )', diff)
        sheaders = [str(h.header).strip() for h in hunks]; gheaders = [h.splitlines()[0].strip() for h in ghunks]
        if [x.split('@@')[1] for x in sheaders] != [x.split('@@')[1] for x in gheaders]:
            bad.append((case, 'headers', sheaders[:2], gheaders[:2])); continue
        pick = sorted(rnd.sample(range(len(hunks)), rnd.randint(1, len(hunks))))
        s.commit(a, message='some', hunks=[str(hunks[i].hunk_id) for i in pick])
        git(g, 'apply', '--cached', inp=head + ''.join(ghunks[i] for i in pick))
        expect = git(g, 'show', ':m.py'); total += 1
        if committed(s, a)['m.py'] != expect: bad.append((case, 'content', pick))
        if get(a, 'm.py') != work: bad.append((case, 'working copy written'))
    return not bad, f'{total} hunk subsets committed; differences: {bad[:3] or "none"}'

@check('C3', (0, 26, 6), 'a stale hunk id is refused and nothing is written')
def _():
    s, a, _ = vault({'m.py': TEXT})
    put(a, 'm.py', TEXT.replace('line 3\n', 'line 3 x\n'))
    hid = str(s.list_hunks(a, paths=['m.py']).files[0].hunks[0].hunk_id)
    put(a, 'm.py', TEXT.replace('line 3\n', 'line 3 y\n'))
    head, before = s.resolve_revision(a, 'HEAD'), objects(a)
    try: s.commit(a, message='stale', hunks=[hid]); return False, 'accepted'
    except Exception as e:
        return (s.resolve_revision(a, 'HEAD'), objects(a)) == (head, before), f'{type(e).__name__}; HEAD and objects unchanged'

@check('C4', (0, 26, 6), 'push with uncommitted changes pushes the commits and keeps the edits')
def _():
    s, a, key = vault({'x.txt': 'x\n', 'y.txt': 'y\n'})
    put(a, 'x.txt', 'x2\n'); s.commit(a, message='x', paths=['x.txt']); put(a, 'y.txt', 'y local\n')
    s.push(a)
    c = d('c'); s.clone(key, c)
    return get(c, 'x.txt') == 'x2\n' and get(c, 'y.txt') == 'y\n' and get(a, 'y.txt') == 'y local\n', 'remote has x2, y unchanged; y edit kept locally'

@check('C5', (0, 26, 6), 'push refuses before writing when incoming commits would change an edited file')
def _():
    s, a, key = vault({'x.txt': 'x\n', 'y.txt': 'y\n'})
    b = d('b'); s.clone(key, b)
    put(b, 'y.txt', 'y by b\n'); s.commit(b, message='b'); s.push(b)
    put(a, 'x.txt', 'x2\n'); s.commit(a, message='a', paths=['x.txt']); put(a, 'y.txt', 'y local edit\n')
    try: s.push(a); refused = False
    except Exception: refused = True
    return refused and get(a, 'y.txt') == 'y local edit\n', f'refused: {refused}; edit kept: {get(a, "y.txt") == "y local edit\n"}'

# ── report ───────────────────────────────────────────────────────────────────────────────────────────────────
W = 98
print('╔' + '═' * W + '╗')
print(('║  sgit-ai ' + VERSION + ' · end-to-end checks · in-memory host').ljust(W + 1) + '║')
print('╠' + '═' * W + '╣')
icon = {'PASS': '✓', 'FAIL': '✗', 'ERROR': '!', 'n/a': '·'}
for cid, title, st, detail, dt in results:
    print(f'║ {icon[st]} {cid:3} {st:5} {title[:62]:62} {dt:6.1f}s'.ljust(W + 1) + '║')
    if st != 'n/a': print(f'║{" " * 13}└─ {detail[:W - 17]}'.ljust(W + 1) + '║')
c = {k: sum(1 for r in results if r[2] == k) for k in icon}
print('╠' + '═' * W + '╣')
print(f'║  {c["PASS"]} pass · {c["FAIL"]} fail · {c["ERROR"]} error · {c["n/a"]} not claimed by this build'.ljust(W + 1) + '║')
print('╚' + '═' * W + '╝')
if len(sys.argv) > 1:
    json.dump({'version': VERSION, 'results': [dict(zip(('id', 'title', 'status', 'detail', 'seconds'), r)) for r in results]},
              open(sys.argv[1], 'w'), indent=1)
