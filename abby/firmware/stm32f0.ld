/*
 * Running from RAM
 * change the ORIGIN value of rom to 0x20000000
 * change the LENGTH value of rom to "< 8K" (e.g. 4K)
 * change the ORIGIN value of ram to "0x20000000 + <length of rom memory region>"
 * change the LENGTH value of ram to "8K - <origin of ram memory region>"
 */

MEMORY
{
        rom (rx) : ORIGIN = 0x20000000, LENGTH = 6K
        ram (rwx) : ORIGIN = 0x20001800, LENGTH = 2K
}

INCLUDE cortex-m-generic.ld
