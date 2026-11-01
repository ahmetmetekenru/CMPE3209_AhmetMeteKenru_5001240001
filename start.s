    .text
    .globl _start
_start:
    call main
    li a7, 10       # Ripes/RARS exit ecall
    ecall
