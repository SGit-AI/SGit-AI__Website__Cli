from common import *
import pyoxigraph as ox, shutil, zlib
E = 'urn:v:'
def node(x): return ox.NamedNode(E + x.replace(' ', '%20'))
LIT = {'ts', 'size'}
path = f'{GX}/oxi'; shutil.rmtree(path, ignore_errors=True)
t = time.perf_counter()
st = ox.Store(path)
quads = [ox.Quad(node(s), ox.NamedNode(E + 'p/' + p), ox.Literal(o, datatype=ox.NamedNode('http://www.w3.org/2001/XMLSchema#integer')) if p in LIT else node(o)) for s, p, o in T]
st.bulk_extend(quads); st.optimize(); st.flush()
load = time.perf_counter() - t
size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(path) for f in fs)
nt = '\n'.join(f'<{E}{s}> <{E}p/{p}> ' + (f'"{o}"' if p in LIT else f'<{E}{o}>') + ' .' for s, p, o in T).encode()
PFX = f'PREFIX v: <{E}> PREFIX p: <{E}p/> '
def one(qs):
    r = list(st.query(PFX + qs)); return r
def cnt(qs): return int(one(qs)[0][0].value)
import signal
class TO(Exception): pass
def _alarm(*a): raise TO()
signal.signal(signal.SIGALRM, _alarm)
_timed = timed
def timed(fn, n=None):
    signal.alarm(60)
    try: return _timed(fn, n)
    except TO: print('    .. over 60 s'); return ('timeout', 60.0)
    finally: signal.alarm(0)
R = {}
R['children']          = timed(lambda: cnt(f'SELECT (COUNT(?c) AS ?n) WHERE {{ <{E}d:{M["folder_deep"]}> p:contains ?c }}'))
R['subtree_files']     = timed(lambda: cnt(f'SELECT (COUNT(?f) AS ?n) WHERE {{ <{E}d:{M["folder"]}> p:contains+ ?f . ?f p:blob ?b }}'))
R['file_to_root']      = timed(lambda: cnt(f'SELECT (COUNT(?d) AS ?n) WHERE {{ ?d p:contains+ <{E}f:{M["file"]}> }}'))
R['ancestors_of_head'] = timed(lambda: cnt(f'SELECT (COUNT(?a) AS ?n) WHERE {{ <{E}{M["head"]}> p:parent+ ?a }}'))
R['merge_base']        = timed(lambda: one(f'SELECT ?c WHERE {{ {{ SELECT DISTINCT ?c WHERE {{ <{E}{M["head"]}> p:parent* ?c }} }} {{ SELECT DISTINCT ?c WHERE {{ <{E}{M["side_tip"]}> p:parent* ?c }} }} ?c p:ts ?t }} ORDER BY DESC(?t) LIMIT 1')[0][0].value[len(E):])
R['base_to_head']      = timed(lambda: cnt(f'SELECT (COUNT(?c) AS ?n) WHERE {{ <{E}{M["head"]}> p:parent* ?c . MINUS {{ SELECT DISTINCT ?c WHERE {{ <{E}{M["base"]}> p:parent* ?c }} }} }}'))
R['file_history']      = timed(lambda: cnt(f'SELECT (COUNT(?c) AS ?n) WHERE {{ ?c p:changed <{E}f:{M["file"]}> }}'))
R['paths_of_blob']     = timed(lambda: cnt(f'SELECT (COUNT(?f) AS ?n) WHERE {{ ?f p:blob <{E}{M["blob"]}> }}'))
report('Oxigraph, SPARQL (pyoxigraph, Rust wheel)', load, size, R, f'N-Triples {len(nt)/1e6:.0f} MB, deflated {len(zlib.compress(nt,6))/1e6:.1f} MB')
