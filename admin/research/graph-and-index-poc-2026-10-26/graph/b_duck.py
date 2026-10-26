from common import *
import duckdb, csv, signal
path = f'{GX}/duck.db'
if os.path.exists(path): os.remove(path)
with open(f'{GX}/csv/triples.csv', 'w', newline='') as f: csv.writer(f).writerows(T)
t = time.perf_counter()
db = duckdb.connect(path)
db.execute(f"CREATE TABLE t AS SELECT * FROM read_csv('{GX}/csv/triples.csv', header=false, columns={{'s':'VARCHAR','p':'VARCHAR','o':'VARCHAR'}})")
db.execute('CHECKPOINT'); load = time.perf_counter() - t
size = os.path.getsize(path)
q = lambda sql, *a: db.execute(sql, list(a)).fetchall()
class TO(Exception): pass
def _alarm(*a): raise TO()
signal.signal(signal.SIGALRM, _alarm)
_timed = timed
def timed(fn, n=None):
    signal.alarm(60)
    try: return _timed(fn, n)
    except TO: print('    .. over 60 s'); return ('timeout', 60.0)
    finally: signal.alarm(0)
ANC = lambda start: f"WITH RECURSIVE a(c) AS (SELECT {start} UNION SELECT t.o FROM a JOIN t ON t.p='parent' AND t.s=a.c) "
R = {}
R['children'] = timed(lambda: q("SELECT count(*) FROM t WHERE p='contains' AND s=?", f'd:{M["folder_deep"]}')[0][0])
R['subtree_files'] = timed(lambda: q("""WITH RECURSIVE sub(x) AS (SELECT o FROM t WHERE p='contains' AND s=? UNION ALL
   SELECT t.o FROM sub JOIN t ON t.p='contains' AND t.s=sub.x) SELECT count(*) FROM sub WHERE x LIKE 'f:%'""", f'd:{M["folder"]}')[0][0])
R['file_to_root'] = timed(lambda: q("""WITH RECURSIVE up(x) AS (SELECT s FROM t WHERE p='contains' AND o=? UNION ALL
   SELECT t.s FROM up JOIN t ON t.p='contains' AND t.o=up.x) SELECT count(*) FROM up""", f'f:{M["file"]}')[0][0])
R['ancestors_of_head'] = timed(lambda: q(ANC('?') + 'SELECT count(*) - 1 FROM a', M['head'])[0][0])
R['merge_base'] = timed(lambda: q("WITH RECURSIVE a(c) AS (SELECT ? UNION SELECT t.o FROM a JOIN t ON t.p='parent' AND t.s=a.c), "
   "b(c) AS (SELECT ? UNION SELECT t.o FROM b JOIN t ON t.p='parent' AND t.s=b.c) "
   "SELECT a.c FROM a JOIN b ON a.c=b.c JOIN t ON t.p='ts' AND t.s=a.c ORDER BY CAST(t.o AS BIGINT) DESC LIMIT 1", M['head'], M['side_tip'])[0][0])
R['base_to_head'] = timed(lambda: q("WITH RECURSIVE a(c) AS (SELECT ? UNION SELECT t.o FROM a JOIN t ON t.p='parent' AND t.s=a.c), "
   "b(c) AS (SELECT ? UNION SELECT t.o FROM b JOIN t ON t.p='parent' AND t.s=b.c) SELECT count(*) FROM (SELECT c FROM a EXCEPT SELECT c FROM b)", M['head'], M['base'])[0][0])
R['file_history'] = timed(lambda: q("SELECT count(*) FROM t WHERE p='changed' AND o=?", f'f:{M["file"]}')[0][0])
R['paths_of_blob'] = timed(lambda: q("SELECT count(*) FROM t WHERE p='blob' AND o=?", M['blob'])[0][0])
report(f'DuckDB {duckdb.__version__}, SQL recursive CTE (wheel)', load, size, R)
