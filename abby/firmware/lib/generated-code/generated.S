.syntax unified
.thumb

# Data section
.data
.balign 4
a: .skip 400  /* 100*4 (int) */

# Code section
.text
.func generated_code
.global generated_code
generated_code:
    mov r5, lr
    push {r0-r7}
    ldr r0, addr_a
    bl next_a
    .balign 4
addr_a:
    .word a
next_a:
#include GENERATED_PATH
    pop {r0-r7}
bx r5
.endfunc
