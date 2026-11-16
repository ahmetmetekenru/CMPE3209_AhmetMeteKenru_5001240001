"""CMPE3209 G3 tools (Ahmet Mete Kenru, 5001240001)

1) Data address trace: runs an RV32IM ELF instruction by instruction and logs every lw/sw
   python3 cachesim.py --trace main.elf main.c trace.csv
   (main.c is recompiled with -g only to look up C line numbers; needs riscv64-unknown-elf-gcc)
2) Cache simulation (set-associative, LRU, write-through + write-allocate)
   python3 cachesim.py trace.csv SIZE LINE WAYS [N]      e.g. trace.csv 128 16 2 30
"""
import sys, csv, subprocess, tempfile, os

# ---------- 1) trace generator ----------
def make_trace(elf, src, out):
    mem = {}
    def load(sec, base):
        t = tempfile.mktemp()
        subprocess.run(['riscv64-unknown-elf-objcopy', '-O', 'binary', '-j', sec, elf, t], check=True)
        for i, v in enumerate(open(t, 'rb').read()): mem[base + i] = v
    load('.text', 0); load('.sdata', 0x10000000)
    rd = lambda a: sum(mem.get(a + i, 0) << (8 * i) for i in range(4))
    def wr(a, v):
        for i in range(4): mem[a + i] = (v >> (8 * i)) & 255
    gelf = tempfile.mktemp()
    opt = '-O1' if 'O1' in elf else '-O0'
    subprocess.run(['riscv64-unknown-elf-gcc', '-march=rv32im', '-mabi=ilp32', opt, '-g', '-nostdlib', '-ffreestanding',
                    '-Wl,--no-relax-gp', '-Wl,-Ttext=0x0', '-Wl,-Tdata=0x10000000',
                    os.path.join(os.path.dirname(os.path.abspath(src)), 'start.s'), src, '-o', gelf], check=True)
    dis = subprocess.run(['riscv64-unknown-elf-objdump', '-d', elf], capture_output=True, text=True).stdout
    pcs = sorted({int(l.split(':')[0], 16) for l in dis.splitlines()
                  if l.startswith(' ') and ':' in l and all(c in '0123456789abcdef' for c in l.split(':')[0].strip())})
    a2l = subprocess.run(['riscv64-unknown-elf-addr2line', '-e', gelf] + [hex(p) for p in pcs],
                         capture_output=True, text=True).stdout.strip().split('\n')
    line = {p: (l.split(':')[-1].split()[0] if '.c' in l else 'start.s') for p, l in zip(pcs, a2l)}
    sx = lambda v, b: v - (1 << b) if v >> (b - 1) & 1 else v
    R = [0] * 32; R[2] = 0x7ffffff0; pc = 0; M = 0xffffffff; trace = []; ic = 0
    while True:
        ins = rd(pc); op = ins & 127; rdd = (ins >> 7) & 31; f3 = (ins >> 12) & 7
        a = R[(ins >> 15) & 31]; b = R[(ins >> 20) & 31]; f7 = ins >> 25; npc = pc + 4; w = None; ic += 1
        if op == 0x37: w = ins & 0xfffff000
        elif op == 0x17: w = (pc + (ins & 0xfffff000)) & M
        elif op == 0x13:
            im = sx(ins >> 20, 12); sh = (ins >> 20) & 31
            w = {0: a + im, 2: int(sx(a, 32) < im), 3: int(a < (im & M)), 4: a ^ (im & M), 6: a | (im & M),
                 7: a & (im & M), 1: a << sh, 5: (a >> sh) if not f7 else (sx(a, 32) >> sh)}[f3] & M
        elif op == 0x33 and f7 == 1: w = {0: (a * b) & M, 7: a % b if b else a, 5: a // b if b else M}[f3]
        elif op == 0x33:
            w = {0: (a - b) if f7 else (a + b), 1: a << (b & 31), 4: a ^ b, 5: a >> (b & 31), 6: a | b, 7: a & b,
                 2: int(sx(a, 32) < sx(b, 32)), 3: int(a < b)}[f3] & M
        elif op == 0x03:
            ad = (a + sx(ins >> 20, 12)) & M; w = rd(ad); trace.append(('R', ad, pc))
        elif op == 0x23:
            ad = (a + sx(((ins >> 25) << 5) | ((ins >> 7) & 31), 12)) & M; wr(ad, b); trace.append(('W', ad, pc))
        elif op == 0x6f:
            im = sx(((ins >> 31) << 20) | (((ins >> 12) & 255) << 12) | (((ins >> 20) & 1) << 11) | (((ins >> 21) & 1023) << 1), 21)
            w = npc; npc = (pc + im) & M
        elif op == 0x67: w = npc; npc = (a + sx(ins >> 20, 12)) & ~1 & M
        elif op == 0x63:
            im = sx(((ins >> 31) << 12) | (((ins >> 7) & 1) << 11) | (((ins >> 25) & 63) << 5) | (((ins >> 8) & 15) << 1), 13)
            if {0: a == b, 1: a != b, 4: sx(a, 32) < sx(b, 32), 5: sx(a, 32) >= sx(b, 32), 6: a < b, 7: a >= b}[f3]: npc = (pc + im) & M
        elif op == 0x73: break                                   # ecall: program exit
        else: raise ValueError(hex(ins))
        if w is not None and rdd: R[rdd] = w & M
        pc = npc
    with open(out, 'w') as f:
        f.write('sira,RW,adres_hex,boyut,c_satiri,stack_mi\n')
        for i, (rw, ad, p) in enumerate(trace, 1):
            f.write(f'{i},{rw},0x{ad:08X},4,{line[p]},{"yes" if ad >= 0x7f000000 else "no"}\n')
    print(f'instructions={ic} data_refs={len(trace)} -> {out}')

# ---------- 2) cache simulator ----------
def run(trace, size=128, line=16, ways=2, n=None):
    sets = size // line // ways
    slots = [[None] * ways for _ in range(sets)]   # physical lines of each set (tags)
    lru = [[] for _ in range(sets)]                # way indices, least recently used first
    hits = misses = memw = 0; rows = []; seen = set()
    for k, (rw, addr) in enumerate(trace[:n] if n else trace, 1):
        blk = addr // line; s = blk % sets; tag = blk // sets; ev = None
        if tag in slots[s]:
            hits += 1; res = 'Hit'; way = slots[s].index(tag)
        else:
            misses += 1; res = 'Miss'
            if None in slots[s]: way = slots[s].index(None)
            else: way = lru[s][0]; ev = slots[s][way] * sets + s
            slots[s][way] = tag                    # write-allocate
        if way in lru[s]: lru[s].remove(way)
        lru[s].append(way)
        if rw == 'W': memw += 1                    # write-through: every store also writes memory
        rows.append(dict(k=k, rw=rw, addr=addr, tag=tag, set=s, word=addr % line, res=res, ev=ev, before=blk in seen))
        seen.add(blk)
    return dict(hits=hits, misses=misses, H=hits / (hits + misses), memw=memw, rows=rows, slots=slots, lru=lru, sets=sets, ways=ways)

def load(path):
    return [(r['RW'], int(r['adres_hex'], 16)) for r in csv.DictReader(open(path))]

if __name__ == '__main__':
    if sys.argv[1] == '--trace':
        make_trace(*sys.argv[2:5]); sys.exit()
    t = load(sys.argv[1]); size, line, ways = map(int, sys.argv[2:5]); n = int(sys.argv[5]) if len(sys.argv) > 5 else None
    r = run(t, size, line, ways, n)
    print(f"refs={r['hits']+r['misses']} hits={r['hits']} misses={r['misses']} H={r['H']:.4f} mem_writes={r['memw']}")
    if n:
        print(f"cache state after reference {n}:")
        for s in range(r['sets']):
            cells = [f"line {s*ways+w}: " + (f"V=1 tag=0x{r['slots'][s][w]:07X}" if r['slots'][s][w] is not None else "V=0") for w in range(ways)]
            print(f"  set {s}:  " + '   '.join(f"{c:<26}" for c in cells) + "  LRU->MRU: " + (', '.join(f"line {s*ways+w}" for w in r['lru'][s]) or '-'))
