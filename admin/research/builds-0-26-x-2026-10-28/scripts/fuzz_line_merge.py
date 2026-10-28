# Differential fuzz: sgit's Vault__Line_Merge against `git merge-file -p`, on random three-way inputs.
#   python -I fuzz_line_merge.py <seed> <cases> [merge|diff3]
# Run with the Python of an installed sgit-ai >= 0.26.5. Needs git on PATH.
import os, sys, random, subprocess, tempfile, json, collections
from sgit_ai.core.text.Vault__Line_Merge      import Vault__Line_Merge
from sgit_ai.safe_types.Enum__Conflict_Style  import Enum__Conflict_Style
from sgit_ai.safe_types.Enum__Line_Merge_Outcome import Enum__Line_Merge_Outcome
SEED, N = int(sys.argv[1]), int(sys.argv[2]); STYLE = sys.argv[3] if len(sys.argv) > 3 else 'merge'
rnd = random.Random(SEED); lm = Vault__Line_Merge(); tmp = tempfile.mkdtemp()
style = Enum__Conflict_Style.DIFF3 if STYLE == 'diff3' else Enum__Conflict_Style.MERGE
CODE = ['}', '', '{', '    return x;', '    i++;', 'end', '#', '  ', 'else', '    }', 'if (a) {', 'x = 1;']
uid = [0]
def fresh():
    uid[0] += 1; return f'line {uid[0]} {rnd.random():.6f}'
def make(kind, n):
    if kind == 'unique': return [fresh() for _ in range(n)]
    if kind == 'code':   return [rnd.choice(CODE) if rnd.random() < .6 else fresh() for _ in range(n)]
    return [rnd.choice('abc') for _ in range(n)]                                   # 'tiny': three letters, worst case
def edit(lines, kind):
    out = list(lines)
    for _ in range(rnd.randint(0, 4)):
        op = rnd.random(); i = rnd.randint(0, len(out))
        new = make(kind, rnd.randint(1, 3))
        if op < .35 and out:   del out[i:i + rnd.randint(1, 3)]
        elif op < .7:          out[i:i] = new
        elif out:              out[i:i + rnd.randint(1, 2)] = new
    return out
def render(lines, crlf, final_nl):
    eol = '\r\n' if crlf else '\n'
    s = eol.join(lines)
    return (s + eol if (lines and final_nl) else s).encode()
stats = collections.Counter(); samples = collections.defaultdict(list)
for case in range(N):
    kind = rnd.choice(['unique', 'unique', 'code', 'tiny'])
    base = make(kind, rnd.randint(0, 25)); ours, theirs = edit(base, kind), edit(base, kind)
    crlf = rnd.random() < .15
    b, o, t = (render(x, crlf, rnd.random() > .2) for x in (base, ours, theirs))
    out, res = lm.merge(b, o, t, conflict_style=style)
    paths = []
    for name, data in (('ours', o), ('base', b), ('theirs', t)):
        p = os.path.join(tmp, name); open(p, 'wb').write(data); paths.append(p)
    cmd = ['git', 'merge-file', '-p', '-L', 'ours', '-L', 'base', '-L', 'theirs'] + (['--diff3'] if STYLE == 'diff3' else []) + paths
    g = subprocess.run(cmd, capture_output=True)
    s_conf = res.outcome == Enum__Line_Merge_Outcome.CONFLICT; g_conf = g.returncode > 0
    if res.outcome not in (Enum__Line_Merge_Outcome.CLEAN, Enum__Line_Merge_Outcome.CONFLICT):
        verdict = f'not merged ({res.outcome})'
    elif out == g.stdout and int(res.hunks or 0) == min(g.returncode, 127): verdict = 'identical'
    elif out == g.stdout:                                                 verdict = 'same bytes, other hunk count'
    elif not s_conf and g_conf:                                           verdict = 'sgit clean, git conflict'
    elif s_conf and not g_conf:                                           verdict = 'sgit conflict, git clean'
    elif not s_conf:                                                      verdict = 'both clean, bytes differ'
    else:                                                                 verdict = 'both conflict, bytes differ'
    stats[(kind, verdict)] += 1
    if verdict != 'identical' and len(samples[verdict]) < 3:
        samples[verdict].append({'case': case, 'kind': kind, 'crlf': crlf, 'base': b.decode(), 'ours': o.decode(), 'theirs': t.decode(),
                                 'sgit': out.decode(errors='replace'), 'git': g.stdout.decode(errors='replace')})
kinds = ['unique', 'code', 'tiny']; verdicts = sorted({v for _, v in stats})
w = max(len(v) for v in verdicts) + 2
print('┌' + '─' * (w + 34) + '┐')
print(f'│ line merge vs git merge-file · {STYLE:5} · seed {SEED:<5} · {N} cases'.ljust(w + 35) + '│')
print('├' + '─' * (w + 34) + '┤')
print('│ ' + 'verdict'.ljust(w) + ''.join(k.rjust(10) for k in kinds) + '   │')
for v in verdicts:
    mark = '✓' if v == 'identical' else ('✗' if v.startswith('sgit clean') or v.startswith('both clean') else '·')
    print(f'│{mark}' + v.ljust(w) + ''.join(str(stats[(k, v)]).rjust(10) for k in kinds) + '   │')
print('└' + '─' * (w + 34) + '┘')
out = os.environ.get('OUT')
if out: json.dump({'seed': SEED, 'cases': N, 'style': STYLE, 'stats': {f'{k}|{v}': c for (k, v), c in stats.items()}, 'samples': samples}, open(out, 'w'), indent=1)
