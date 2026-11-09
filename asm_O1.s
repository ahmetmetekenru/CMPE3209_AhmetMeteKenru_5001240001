	.file	"main.c"
	.option nopic
	.attribute arch, "rv32i2p1_m2p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
	.text
	.align	2
	.globl	rotl
	.type	rotl, @function
rotl:
	sll	a5,a0,a1
	neg	a1,a1
	srl	a0,a0,a1
	or	a0,a0,a5
	ret
	.size	rotl, .-rotl
	.align	2
	.globl	main
	.type	main, @function
main:
	lui	a2,%hi(.LANCHOR0)
	addi	a3,a2,%lo(.LANCHOR0)
	addi	a0,a3,100
	mv	a6,a0
	mv	a1,a0
	addi	a2,a2,%lo(.LANCHOR0)
	li	a4,1241088
	addi	a4,a4,-1087
	li	t1,1662976
	addi	t1,t1,1549
	li	a7,1013903360
	addi	a7,a7,863
	li	t3,26
.L3:
	mul	a4,a4,t1
	add	a4,a4,a7
	srli	a5,a4,16
	remu	a5,a5,t3
	addi	a5,a5,65
	sw	a5,0(a2)
	sw	a5,0(a1)
	addi	a2,a2,4
	addi	a1,a1,4
	bne	a2,a6,.L3
	mv	a4,a3
	li	a5,0
.L4:
	lw	a2,0(a4)
	xori	a2,a2,193
	sw	a2,0(a4)
	slli	a1,a5,1
	srli	a5,a5,31
	or	a5,a1,a5
	add	a5,a5,a2
	addi	a4,a4,4
	bne	a4,a6,.L4
	lui	a4,%hi(checksum)
	sw	a5,%lo(checksum)(a4)
	lui	a5,%hi(decrypt_ok)
	li	a4,1
	sw	a4,%lo(decrypt_ok)(a5)
	li	a2,0
	li	a1,1
	j	.L6
.L5:
	addi	a3,a3,4
	addi	a0,a0,4
	beq	a3,a6,.L11
.L6:
	lw	a5,0(a3)
	xori	a5,a5,193
	sw	a5,0(a3)
	lw	a4,0(a0)
	beq	a5,a4,.L5
	mv	a2,a1
	j	.L5
.L11:
	beq	a2,zero,.L7
	lui	a5,%hi(decrypt_ok)
	sw	zero,%lo(decrypt_ok)(a5)
.L7:
	li	a0,0
	ret
	.size	main, .-main
	.globl	decrypt_ok
	.globl	checksum
	.globl	orig
	.globl	msg
	.globl	SID
	.bss
	.align	2
	.set	.LANCHOR0,. + 0
	.type	msg, @object
	.size	msg, 100
msg:
	.zero	100
	.type	orig, @object
	.size	orig, 100
orig:
	.zero	100
	.section	.sbss,"aw",@nobits
	.align	2
	.type	decrypt_ok, @object
	.size	decrypt_ok, 4
decrypt_ok:
	.zero	4
	.type	checksum, @object
	.size	checksum, 4
checksum:
	.zero	4
	.section	.srodata,"a"
	.align	2
	.type	SID, @object
	.size	SID, 4
SID:
	.word	1240001
	.ident	"GCC: (13.2.0-11ubuntu1+12) 13.2.0"
