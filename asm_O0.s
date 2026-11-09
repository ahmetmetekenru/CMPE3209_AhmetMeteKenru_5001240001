	.file	"main.c"
	.option nopic
	.attribute arch, "rv32i2p1_m2p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
	.text
	.globl	SID
	.section	.srodata,"a"
	.align	2
	.type	SID, @object
	.size	SID, 4
SID:
	.word	1240001
	.globl	msg
	.bss
	.align	2
	.type	msg, @object
	.size	msg, 100
msg:
	.zero	100
	.globl	orig
	.align	2
	.type	orig, @object
	.size	orig, 100
orig:
	.zero	100
	.globl	checksum
	.section	.sbss,"aw",@nobits
	.align	2
	.type	checksum, @object
	.size	checksum, 4
checksum:
	.zero	4
	.globl	decrypt_ok
	.align	2
	.type	decrypt_ok, @object
	.size	decrypt_ok, 4
decrypt_ok:
	.zero	4
	.text
	.align	2
	.globl	rotl
	.type	rotl, @function
rotl:
	addi	sp,sp,-32
	sw	s0,28(sp)
	addi	s0,sp,32
	sw	a0,-20(s0)
	sw	a1,-24(s0)
	lw	a5,-20(s0)
	lw	a4,-24(s0)
	sll	a4,a5,a4
	lw	a3,-24(s0)
	neg	a3,a3
	andi	a3,a3,31
	srl	a5,a5,a3
	or	a5,a5,a4
	mv	a0,a5
	lw	s0,28(sp)
	addi	sp,sp,32
	jr	ra
	.size	rotl, .-rotl
	.align	2
	.globl	main
	.type	main, @function
main:
	addi	sp,sp,-32
	sw	ra,28(sp)
	sw	s0,24(sp)
	addi	s0,sp,32
	li	a5,1241088
	addi	a5,a5,-1087
	sw	a5,-20(s0)
	li	a5,1241088
	addi	a5,a5,-1087
	andi	a5,a5,255
	sw	a5,-24(s0)
	lw	a5,-24(s0)
	bne	a5,zero,.L4
	li	a5,165
	sw	a5,-24(s0)
.L4:
	sw	zero,-28(s0)
	j	.L5
.L6:
	lw	a4,-20(s0)
	li	a5,1662976
	addi	a5,a5,1549
	mul	a4,a4,a5
	li	a5,1013903360
	addi	a5,a5,863
	add	a5,a4,a5
	sw	a5,-20(s0)
	lw	a5,-20(s0)
	srli	a4,a5,16
	li	a5,26
	remu	a5,a4,a5
	addi	a5,a5,65
	mv	a3,a5
	lui	a5,%hi(msg)
	addi	a4,a5,%lo(msg)
	lw	a5,-28(s0)
	slli	a5,a5,2
	add	a5,a4,a5
	sw	a3,0(a5)
	lui	a5,%hi(msg)
	addi	a4,a5,%lo(msg)
	lw	a5,-28(s0)
	slli	a5,a5,2
	add	a5,a4,a5
	lw	a4,0(a5)
	lui	a5,%hi(orig)
	addi	a3,a5,%lo(orig)
	lw	a5,-28(s0)
	slli	a5,a5,2
	add	a5,a3,a5
	sw	a4,0(a5)
	lw	a5,-28(s0)
	addi	a5,a5,1
	sw	a5,-28(s0)
.L5:
	lw	a4,-28(s0)
	li	a5,24
	ble	a4,a5,.L6
	lui	a5,%hi(checksum)
	sw	zero,%lo(checksum)(a5)
	sw	zero,-28(s0)
	j	.L7
.L8:
	lui	a5,%hi(msg)
	addi	a4,a5,%lo(msg)
	lw	a5,-28(s0)
	slli	a5,a5,2
	add	a5,a4,a5
	lw	a4,0(a5)
	lw	a5,-24(s0)
	xor	a4,a4,a5
	lui	a5,%hi(msg)
	addi	a3,a5,%lo(msg)
	lw	a5,-28(s0)
	slli	a5,a5,2
	add	a5,a3,a5
	sw	a4,0(a5)
	lui	a5,%hi(checksum)
	lw	a5,%lo(checksum)(a5)
	li	a1,1
	mv	a0,a5
	call	rotl
	mv	a3,a0
	lui	a5,%hi(msg)
	addi	a4,a5,%lo(msg)
	lw	a5,-28(s0)
	slli	a5,a5,2
	add	a5,a4,a5
	lw	a5,0(a5)
	add	a4,a3,a5
	lui	a5,%hi(checksum)
	sw	a4,%lo(checksum)(a5)
	lw	a5,-28(s0)
	addi	a5,a5,1
	sw	a5,-28(s0)
.L7:
	lw	a4,-28(s0)
	li	a5,24
	ble	a4,a5,.L8
	lui	a5,%hi(decrypt_ok)
	li	a4,1
	sw	a4,%lo(decrypt_ok)(a5)
	sw	zero,-28(s0)
	j	.L9
.L11:
	lui	a5,%hi(msg)
	addi	a4,a5,%lo(msg)
	lw	a5,-28(s0)
	slli	a5,a5,2
	add	a5,a4,a5
	lw	a4,0(a5)
	lw	a5,-24(s0)
	xor	a4,a4,a5
	lui	a5,%hi(msg)
	addi	a3,a5,%lo(msg)
	lw	a5,-28(s0)
	slli	a5,a5,2
	add	a5,a3,a5
	sw	a4,0(a5)
	lui	a5,%hi(msg)
	addi	a4,a5,%lo(msg)
	lw	a5,-28(s0)
	slli	a5,a5,2
	add	a5,a4,a5
	lw	a4,0(a5)
	lui	a5,%hi(orig)
	addi	a3,a5,%lo(orig)
	lw	a5,-28(s0)
	slli	a5,a5,2
	add	a5,a3,a5
	lw	a5,0(a5)
	beq	a4,a5,.L10
	lui	a5,%hi(decrypt_ok)
	sw	zero,%lo(decrypt_ok)(a5)
.L10:
	lw	a5,-28(s0)
	addi	a5,a5,1
	sw	a5,-28(s0)
.L9:
	lw	a4,-28(s0)
	li	a5,24
	ble	a4,a5,.L11
	li	a5,0
	mv	a0,a5
	lw	ra,28(sp)
	lw	s0,24(sp)
	addi	sp,sp,32
	jr	ra
	.size	main, .-main
	.ident	"GCC: (13.2.0-11ubuntu1+12) 13.2.0"
