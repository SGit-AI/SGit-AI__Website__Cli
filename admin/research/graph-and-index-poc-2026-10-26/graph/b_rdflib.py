from common import *
import rdflib, signal
from rdflib import URIRef, Literal
E = 'urn:v:'; P = lambda p: URIRef(E + 'p/' + p); N = lambda x: URIRef(E + x.replace(' ', '%20'))
t = time.perf_counter()
g = rdflib.Graph()
for s, p, o in T: g.add((N(s), P(p), Literal(int(o)) if p in ('ts', 'size') else N(o)))
load = time.perf_counter() - t
class TO(Exception): pass
def _alarm(*a): raise TO()
signal.signal(signal.SIGALRM, _alarm)
_timed = timed
def timed(fn, n=None):
    signal.alarm(60)
    try: return _timed(fn, n)
    except TO: print('    .. over 60 s'); return ('timeout', 60.0)
    except RecursionError: print('    .. RecursionError'); return ('RecursionError', 0)
    finally: signal.alarm(0)
PFX = f'PREFIX p: <{E}p/> '
cnt = lambda qs: int(list(g.query(PFX + qs))[0][0])
R = {}
R['children']          = timed(lambda: cnt(f'SELECT (COUNT(?c) AS ?n) WHERE {{ <{E}d:{M["folder_deep"]}> p:contains ?c }}'))
R['subtree_files']     = timed(lambda: cnt(f'SELECT (COUNT(?f) AS ?n) WHERE {{ <{E}d:{M["folder"]}> p:contains+ ?f . ?f p:blob ?b }}'))
R['file_to_root']      = timed(lambda: cnt(f'SELECT (COUNT(?d) AS ?n) WHERE {{ ?d p:contains+ <{E}f:{M["file"]}> }}'))
R['ancestors_of_head'] = timed(lambda: cnt(f'SELECT (COUNT(?a) AS ?n) WHERE {{ <{E}{M["head"]}> p:parent+ ?a }}'))
R['merge_base']        = timed(lambda: str(list(g.query(PFX + f'SELECT ?c WHERE {{ {{ SELECT DISTINCT ?c WHERE {{ <{E}{M["head"]}> p:parent* ?c }} }} {{ SELECT DISTINCT ?c WHERE {{ <{E}{M["side_tip"]}> p:parent* ?c }} }} ?c p:ts ?t }} ORDER BY DESC(?t) LIMIT 1'))[0][0])[len(E):])
R['base_to_head']      = timed(lambda: cnt(f'SELECT (COUNT(?c) AS ?n) WHERE {{ <{E}{M["head"]}> p:parent* ?c . MINUS {{ SELECT DISTINCT ?c WHERE {{ <{E}{M["base"]}> p:parent* ?c }} }} }}'))
R['file_history']      = timed(lambda: cnt(f'SELECT (COUNT(?c) AS ?n) WHERE {{ ?c p:changed <{E}f:{M["file"]}> }}'))
R['paths_of_blob']     = timed(lambda: cnt(f'SELECT (COUNT(?f) AS ?n) WHERE {{ ?f p:blob <{E}{M["blob"]}> }}'))
report(f'rdflib {rdflib.__version__}, SPARQL (pure Python, in memory)', load, None, R)
