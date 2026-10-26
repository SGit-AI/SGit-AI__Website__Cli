import os, sys, random
root = sys.argv[1]; random.seed(7); n = 0
for c in range(10):
  for s in range(5):
    for p in range(20):
      for pg in range(19):
        for t in range(2):
          d = os.path.join(root, 'raw', f'c{c:02d}', f's{s}', f'pub{p:02d}', f'page{pg:02d}', f'2026-10-{20+t}T0{t}00Z')
          os.makedirs(d, exist_ok=True)
          open(os.path.join(d, 'meta.json'), 'w').write('{"country":"c%02d","sector":%d,"publisher":%d,"page":%d,"t":%d,"r":%d}\n' % (c, s, p, pg, t, random.randint(0, 10**9)))
          open(os.path.join(d, 'text.md'), 'w').write(('line %d of page %d\n' % (random.randint(0,10**6), pg)) * 12)
          n += 2
print(n, 'files')
