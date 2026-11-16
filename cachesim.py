"""Data-cache simulator for CMPE3209 (set-associative, LRU, write-through + write-allocate).
usage: python3 cachesim.py trace.csv SIZE LINE WAYS [N]   (N = only the first N references)"""
import sys, csv
def run(trace, size=128, line=16, ways=2, n=None):
    sets = size // line // ways
    slots = [[None] * ways for _ in range(sets)]   # physical lines of each set (tags)
    lru = [[] for _ in range(sets)]                # way indices, least recently used first
    hits = misses = memw = 0; rows = []; seen = set()
    for k, (rw, addr) in enumerate(trace[:n] if n else trace, 1):
        blk = addr // line; s = blk % sets; tag = blk // sets; word = addr % line; ev = None
        if tag in slots[s]:
            hits += 1; res = 'Hit'; way = slots[s].index(tag)
        else:
            misses += 1; res = 'Miss'
            if None in slots[s]: way = slots[s].index(None)
            else:
                way = lru[s][0]; ev = slots[s][way] * sets + s      # evicted block number
            slots[s][way] = tag                    # write-allocate: write misses also fill the line
        if way in lru[s]: lru[s].remove(way)
        lru[s].append(way)
        if rw == 'W': memw += 1                    # write-through: every store also writes memory
        rows.append(dict(k=k, rw=rw, addr=addr, tag=tag, set=s, word=word, res=res, ev=ev, before=blk in seen))
        seen.add(blk)
    return dict(hits=hits, misses=misses, H=hits / (hits + misses), memw=memw, rows=rows, slots=slots, lru=lru, sets=sets, ways=ways)
def load(path):
    return [(r['RW'], int(r['adres_hex'], 16)) for r in csv.DictReader(open(path))]
if __name__ == '__main__':
    t = load(sys.argv[1]); size, line, ways = map(int, sys.argv[2:5]); n = int(sys.argv[5]) if len(sys.argv) > 5 else None
    r = run(t, size, line, ways, n)
    print(f"refs={r['hits']+r['misses']} hits={r['hits']} misses={r['misses']} H={r['H']:.4f} mem_writes={r['memw']}")
    if n:
        print(f"cache state after reference {n}:")
        for s in range(r['sets']):
            cells = [f"line {s*ways+w}: " + (f"V=1 tag=0x{r['slots'][s][w]:07X}" if r['slots'][s][w] is not None else "V=0") for w in range(ways)]
            order = ', '.join(f"line {s*ways+w}" for w in r['lru'][s]) or '-'
            print(f"  set {s}:  " + '   '.join(f"{c:<26}" for c in cells) + f"  LRU->MRU: {order}")
