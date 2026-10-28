# 0.26.8's history commands against git as the oracle, on random histories built twice (a git repo and an sgit vault):
#   blame (porcelain), grep (working copy and a revision), log -S / -G, rename detection (diff --name-status -M).
#   python -I diff_history.py SEED_START SEED_COUNT [SGIT_CLI]      needs git on PATH; sgit CLI defaults to the one beside python
import os, sys, random, subprocess, tempfile, shutil, re, json
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
SG = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(sys.executable), 'sgit')
ENV = dict(os.environ, GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_SYSTEM='/dev/null', LC_ALL='C',
           GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t')
VOCAB = ['alpha beta', 'gamma', 'delta needle', 'epsilon', 'TODO fix this', 'return x', 'import os', 'def f():', '    pass',
         'zeta  spaced', 'eta', 'theta needle two', '', 'iota', 'kappa lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma',
         'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega']
def run(argv, cwd, inp=None):
    p = subprocess.run(argv, cwd=cwd, capture_output=True, env=ENV, input=inp)
    return p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')
def history(rnd, n):
    files, ops = {}, []
    for k in range(n):
        step = []
        if not files or rnd.random() < 0.25:
            name = rnd.choice(['src/', 'docs/', '', 'a b/']) + rnd.choice(['x', 'y', 'z', 'w', 'v']) + str(rnd.randint(0, 99)) + rnd.choice(['.py', '.md', '.txt'])
            if name not in files: files[name] = [rnd.choice(VOCAB) for _ in range(rnd.randint(8, 30))]; step.append(('w', name))
        for name in rnd.sample(sorted(files), min(len(files), rnd.randint(1, 2))):
            ls = files[name]
            for _ in range(rnd.randint(1, 3)):
                r = rnd.random()
                if r < .4 and ls: ls[rnd.randrange(len(ls))] = rnd.choice(VOCAB)
                elif r < .8: ls.insert(rnd.randint(0, len(ls)), rnd.choice(VOCAB))
                elif ls: ls.pop(rnd.randrange(len(ls)))
            step.append(('w', name))
        if len(files) > 1 and rnd.random() < 0.3:
            old = rnd.choice(sorted(files)); new = rnd.choice(['src/', 'docs/', '']) + 'r' + str(rnd.randint(0, 99)) + '.txt'
            if new not in files:
                files[new] = files.pop(old)
                if rnd.random() < .5 and files[new]: files[new][rnd.randrange(len(files[new]))] = rnd.choice(VOCAB)
                step.append(('mv', old, new))
        if len(files) > 2 and rnd.random() < 0.1:
            del files[rnd.choice(sorted(files))]; step.append(('rm',))
        ops.append({k: list(v) for k, v in files.items()})
    return ops
def materialise(base, state):
    for r, ds, fs in os.walk(base):
        ds[:] = [x for x in ds if x not in ('.git', '.sg_vault')]
        for f in fs: os.remove(os.path.join(r, f))
    for name, ls in state.items():
        p = os.path.join(base, name); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w').write(''.join(l + '\n' for l in ls))
fails, counts = [], {}
def cmp(seed, what, a, b):
    counts[what] = counts.get(what, [0, 0]); counts[what][0] += 1
    if a != b:
        counts[what][1] += 1
        if len(fails) < 40: fails.append((seed, what, a[:600], b[:600]))
for seed in range(int(sys.argv[1]), int(sys.argv[1]) + int(sys.argv[2])):
    rnd = random.Random(seed); states = history(rnd, rnd.randint(8, 18))
    W = tempfile.mkdtemp(prefix='dh-'); g, v = os.path.join(W, 'g'), os.path.join(W, 'v'); os.makedirs(g)
    run(['git', 'init', '-q', '-b', 'main'], g)
    s = Vault__Sync(crypto=Vault__Crypto(), api=Vault__API__In_Memory().setup()); s.init(v)
    for i, st in enumerate(states):
        materialise(g, st); materialise(v, st)
        run(['git', 'add', '-A'], g); run(['git', 'commit', '-q', '--allow-empty', '-m', f'c{i}'], g)
        try: s.commit(v, message=f'c{i}')
        except Exception as e:
            if 'nothing' not in str(e).lower(): raise
    last = list(states[-1])
    # blame
    for name in last[:4]:
        _, gb, _ = run(['git', 'blame', '-w', '--porcelain', 'HEAD', '--', name], g) if False else run(['git', 'blame', '--porcelain', 'HEAD', '--', name], g)
        _, sb, se = run([SG, 'history', 'blame', '--porcelain', name], v)
        def parse(t):
            summ, cur, out = {}, None, []
            for ln in t.splitlines():
                m = re.match(r'^([0-9a-f]{12,}|obj-cas-imm-[0-9a-f]+) \d+ (\d+)', ln)
                if m: cur = m.group(1); out.append(cur); continue
                if ln.startswith('summary '): summ[cur] = ln[8:]
            return [summ.get(c) for c in out]
        cmp(seed, 'blame (line -> commit message)', parse(gb), parse(sb))
    # grep, working copy and HEAD~2
    for opts in (['-n', 'needle'], ['-c', 'needle'], ['-l', 'alpha'], ['-i', '-n', 'TODO'], ['-w', '-n', 'eta'], ['-v', '-c', 'a'], ['-n', '-e', 'pass', '-e', 'import'],
                 ['-n', '-A1', 'omega'], ['-F', '-n', 'def f()'], ['-n', 'x', '--', '*.py'], ['-o', '-n', 'ne*dle'], ['-L', 'needle'], ['-n', 'zzzz']):
        rc, go, _ = run(['git', 'grep'] + opts, g); rs, so, se = run([SG, 'grep'] + opts , v)
        cmp(seed, 'grep working copy: output + exit code', (rc, go), (rs, so))
    if len(states) > 3:
        for opts in (['-n', 'needle'], ['-c', 'alpha']):
            rc, go, _ = run(['git', 'grep'] + opts + ['HEAD~2'], g); rs, so, _ = run([SG, 'grep'] + opts + ['HEAD~2'], v)
            cmp(seed, 'grep HEAD~2: output + exit code', (rc, go), (rs, so))
    # pickaxe
    for flag in (['-S', 'needle'], ['-S', 'omega'], ['-G', 'pas+'], ['-i', '-S', 'TODO'], ['-S', 'a.*b', '--pickaxe-regex']):
        _, go, _ = run(['git', 'log', '--format=%s', *(['--no-renames'] if os.environ.get('NORENAMES') else [])] + flag, g); _, so, se = run([SG, 'history', 'log', '--oneline'] + flag , v)
        got = [re.sub(r'^\s*\S+\s+(\(HEAD\)\s+)?', '', l).strip() for l in so.splitlines() if l.strip()]
        cmp(seed, 'log -S/-G: commit messages selected', go.split(), [x.split()[0] for x in got if x])
    # renames: each consecutive pair, -M50
    for k in range(1, len(states)):
        _, gr, _ = run(['git', 'diff', '-M50%', '--name-status', f'HEAD~{len(states)-1-k+1}', f'HEAD~{len(states)-1-k}' if len(states)-1-k else 'HEAD'], g)
        _, sr, _ = run([SG, 'history', 'diff', '-M50', f'HEAD~{len(states)-1-k+1}..' + (f'HEAD~{len(states)-1-k}' if len(states)-1-k else 'HEAD')], v)
        gset = sorted(re.sub(r'\s+', ' ', l.replace('\t', ' ')) for l in gr.splitlines() if l.startswith('R'))
        sset = sorted(re.sub(r'\s+', ' ', l.replace(' -> ', ' ').strip()) for l in sr.splitlines() if re.match(r'^R\d+', l))
        cmp(seed, 'rename detection -M50 (score + paths)', gset, sset)
    (print('KEPT', W) if os.environ.get('KEEP') else shutil.rmtree(W, ignore_errors=True))
for what, (n, bad) in counts.items(): print(f'{what:48} {n - bad:>4}/{n:<4} match')
for f in fails[:12]: print('DIFF', f)
json.dump(dict(counts=counts, fails=fails), open(os.environ.get('OUT', os.devnull), 'w'), indent=1)
