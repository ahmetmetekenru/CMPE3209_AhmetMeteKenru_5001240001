# Instruction-level RV32IM interpreter used to produce trace.csv: logs every lw/sw (sira,RW,adres_hex,boyut,c_satiri,stack_mi).
# usage: python3 trace_gen.py main.elf main_g.elf trace.csv   (main_g.elf = same build with -g, used only for C line numbers)
import sys, subprocess, tempfile, json, collections
elf, gelf, out = sys.argv[1], sys.argv[2], sys.argv[3]
mem={}
def load(sec,base):
    t=tempfile.mktemp(); subprocess.run(['riscv64-unknown-elf-objcopy','-O','binary','-j',sec,elf,t],check=True)
    for i,v in enumerate(open(t,'rb').read()): mem[base+i]=v
load('.text',0); load('.sdata',0x10000000)
def rd(a,n=4): return sum(mem.get(a+i,0)<<(8*i) for i in range(n))
def wr(a,v,n=4):
    for i in range(n): mem[a+i]=(v>>(8*i))&255
# pc -> source line
pcs=sorted({int(l.split(':')[0],16) for l in subprocess.run(['riscv64-unknown-elf-objdump','-d',elf],capture_output=True,text=True).stdout.splitlines() if l.strip() and l.strip().split(':')[0].strip() and all(c in '0123456789abcdef' for c in l.split(':')[0].strip()) and l.startswith(' ')})
a2l=subprocess.run(['riscv64-unknown-elf-addr2line','-e',gelf]+[hex(p) for p in pcs],capture_output=True,text=True).stdout.strip().split('\n')
line={p:(l.split(':')[-1].split()[0] if 'main.c' in l else 'start.s') for p,l in zip(pcs,a2l)}
R=[0]*32; R[2]=0x7ffffff0; pc=0; M=0xffffffff
def sx(v,b): return v-(1<<b) if v>>(b-1)&1 else v
trace=[]; cls=collections.Counter(); pcseq=[]
while True:
    ins=rd(pc); op=ins&127; rdd=(ins>>7)&31; f3=(ins>>12)&7; r1=(ins>>15)&31; r2=(ins>>20)&31; f7=ins>>25
    a=R[r1]; b=R[r2]; npc=pc+4; w=None; pcseq.append(pc)
    if op==0x37: w=ins&0xfffff000; cls['ALU']+=1
    elif op==0x17: w=(pc+(ins&0xfffff000))&M; cls['ALU']+=1
    elif op==0x13:
        im=sx(ins>>20,12); sh=r2; cls['ALU']+=1
        w={0:a+im,2:int(sx(a,32)<im),3:int(a<(im&M)),4:a^(im&M),6:a|(im&M),7:a&(im&M),1:a<<sh,5:(a>>sh) if not f7 else (sx(a,32)>>sh)}[f3]&M
    elif op==0x33:
        if f7==1:
            cls['MUL/DIV']+=1
            w={0:(a*b)&M,7:(a%b if b else a),5:(a//b if b else M)}[f3]
        else:
            cls['ALU']+=1
            w={0:(a-b) if f7 else (a+b),1:a<<(b&31),4:a^b,5:a>>(b&31),6:a|b,7:a&b,2:int(sx(a,32)<sx(b,32)),3:int(a<b)}[f3]&M
    elif op==0x03:
        ad=(a+sx(ins>>20,12))&M; w=rd(ad); cls['Load']+=1; trace.append(('R',ad,4,pc))
    elif op==0x23:
        ad=(a+sx(((ins>>25)<<5)|((ins>>7)&31),12))&M; wr(ad,b); cls['Store']+=1; trace.append(('W',ad,4,pc))
    elif op==0x6f:
        im=sx(((ins>>31)<<20)|(((ins>>12)&255)<<12)|(((ins>>20)&1)<<11)|(((ins>>21)&1023)<<1),21); w=npc; npc=(pc+im)&M; cls['Branch/Jump']+=1
    elif op==0x67: w=npc; npc=(a+sx(ins>>20,12))&~1&M; cls['Branch/Jump']+=1
    elif op==0x63:
        im=sx(((ins>>31)<<12)|(((ins>>7)&1)<<11)|(((ins>>25)&63)<<5)|(((ins>>8)&15)<<1),13)
        c={0:a==b,1:a!=b,4:sx(a,32)<sx(b,32),5:sx(a,32)>=sx(b,32),6:a<b,7:a>=b}[f3]
        if c: npc=(pc+im)&M
        cls['Branch/Jump']+=1
    elif op==0x73: cls['ALU']+=1; break   # ecall counted as ALU-class system instr
    else: raise Exception(hex(ins))
    if w is not None and rdd: R[rdd]=w&M
    pc=npc
with open(out,'w') as f:
    f.write('sira,RW,adres_hex,boyut,c_satiri,stack_mi\n')
    for i,(rw,ad,sz,p) in enumerate(trace,1):
        f.write(f'{i},{rw},0x{ad:08X},{sz},{line[p]},{"yes" if ad>=0x7f000000 else "no"}\n')
json.dump({'Ic':len(pcseq),'cls':cls,'checksum':rd(0x10000004),'ok':rd(0x10000008),'ck8':rd(0x10000008),'ck4':rd(0x10000004)},open(out+'.json','w'))
print(len(pcseq),dict(cls),len(trace),hex(rd(0x10000004)),rd(0x10000008))
