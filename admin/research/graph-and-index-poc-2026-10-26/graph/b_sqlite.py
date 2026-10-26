from common import *
import sqlite3, zlib
mode = sys.argv[1]                                        # text | int
path = f'{GX}/triples_{mode}.db'
if os.path.exists(path): os.remove(path)
t = time.perf_counter()
db = sqlite3.connect(path); db.execute('PRAGMA journal_mode=OFF'); db.execute('PRAGMA synchronous=OFF')
if mode == 'text':
    db.execute('CREATE TABLE t(s TEXT, p TEXT, o TEXT)')
    db.executemany('INSERT INTO t VALUES(?,?,?)', T)
    db.execute('CREATE INDEX spo ON t(p, s, o)'); db.execute('CREATE INDEX pos ON t(p, o, s)')
    N = lambda x: x
else:                                                     # dictionary-encoded: every term an integer
    terms = {}
    def tid(x):
        if x not in terms: terms[x] = len(terms) + 1
        return terms[x]
    rows = [(tid(s), tid(p), tid(o)) for s, p, o in T]
    db.execute('CREATE TABLE term(id INTEGER PRIMARY KEY, v TEXT UNIQUE)')
    db.executemany('INSERT INTO term VALUES(?,?)', ((i, v) for v, i in terms.items()))
    db.execute('CREATE TABLE t(s INT, p INT, o INT)')
    db.executemany('INSERT INTO t VALUES(?,?,?)', rows)
    db.execute('CREATE INDEX spo ON t(p, s, o)'); db.execute('CREATE INDEX pos ON t(p, o, s)')
    N = lambda x: terms[x]
db.commit(); db.execute('ANALYZE'); db.execute('VACUUM'); load = time.perf_counter() - t
size = os.path.getsize(path); dz = len(zlib.compress(open(path, 'rb').read(), 6))
P = lambda name: N(name)
q = lambda sql, *a: db.execute(sql, a).fetchall()
ANC = '''WITH RECURSIVE anc(c) AS (SELECT o FROM t WHERE p=? AND s=? UNION SELECT t.o FROM anc CROSS JOIN t ON t.p=? AND t.s=anc.c) '''
R = {}
R['children'] = timed(lambda: q('SELECT count(*) FROM t WHERE p=? AND s=?', P('contains'), N(f'd:{M["folder_deep"]}'))[0][0])
if mode == 'text':
    R['subtree_files'] = timed(lambda: q('''WITH RECURSIVE sub(x) AS (SELECT o FROM t WHERE p='contains' AND s=? UNION ALL
        SELECT t.o FROM sub CROSS JOIN t ON t.p='contains' AND t.s=sub.x) SELECT count(*) FROM sub WHERE x LIKE 'f:%' ''', f'd:{M["folder"]}')[0][0])
else:
    R['subtree_files'] = timed(lambda: q('''WITH RECURSIVE sub(x) AS (SELECT o FROM t WHERE p=? AND s=? UNION ALL
        SELECT t.o FROM sub CROSS JOIN t ON t.p=? AND t.s=sub.x) SELECT count(*) FROM sub JOIN term ON term.id=sub.x WHERE term.v LIKE 'f:%' ''',
        P('contains'), N(f'd:{M["folder"]}'), P('contains'))[0][0])
R['file_to_root'] = timed(lambda: q('''WITH RECURSIVE up(x) AS (SELECT s FROM t WHERE p=? AND o=? UNION ALL
    SELECT t.s FROM up CROSS JOIN t ON t.p=? AND t.o=up.x) SELECT count(*) FROM up''', P('contains'), N(f'f:{M["file"]}'), P('contains'))[0][0])
pa = P('parent')
R['ancestors_of_head'] = timed(lambda: q(ANC + 'SELECT count(*) FROM anc', pa, N(M['head']), pa)[0][0])
def merge_base():
    sql = ('WITH RECURSIVE a(c) AS MATERIALIZED (SELECT ? UNION SELECT t.o FROM a CROSS JOIN t ON t.p=? AND t.s=a.c), '
           'b(c) AS MATERIALIZED (SELECT ? UNION SELECT t.o FROM b CROSS JOIN t ON t.p=? AND t.s=b.c) '
           'SELECT a.c FROM a JOIN b ON a.c=b.c JOIN t ON t.p=? AND t.s=a.c ' +
           ('ORDER BY CAST(t.o AS INT) DESC LIMIT 1' if mode == 'text' else 'JOIN term ON term.id=t.o ORDER BY CAST(term.v AS INT) DESC LIMIT 1'))
    r = q(sql, N(M['head']), pa, N(M['side_tip']), pa, P('ts'))[0][0]
    return r if mode == 'text' else q('SELECT v FROM term WHERE id=?', r)[0][0]
R['merge_base'] = timed(merge_base)
R['base_to_head'] = timed(lambda: q('''WITH RECURSIVE a(c) AS MATERIALIZED (SELECT ? UNION SELECT t.o FROM a CROSS JOIN t ON t.p=? AND t.s=a.c),
    b(c) AS MATERIALIZED (SELECT ? UNION SELECT t.o FROM b CROSS JOIN t ON t.p=? AND t.s=b.c) SELECT count(*) FROM (SELECT c FROM a EXCEPT SELECT c FROM b)''',
    N(M['head']), pa, N(M['base']), pa)[0][0])
R['file_history'] = timed(lambda: q('SELECT count(*) FROM t WHERE p=? AND o=?', P('changed'), N(f'f:{M["file"]}'))[0][0])
R['paths_of_blob'] = timed(lambda: q('SELECT count(*) FROM t WHERE p=? AND o=?', P('blob'), N(M['blob']))[0][0])
report(f'SQLite triples, {mode} (stdlib)', load, size, R, f'deflated {dz/1e6:.1f} MB')
