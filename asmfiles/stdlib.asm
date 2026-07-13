/*
    QUICK MEMORY MAP
    0x00 ... 0x0F - Function throwaway
    0x10 ... 0x9F - Free memory
    0xA0 ... 0xAF - Function arguments
    0xB0 ... 0xDF - Free memory
    0xE0 ... 0xEF - Macro throwaway
    0xF0 ... 0xFE - Reserved
    0xFF          - JMPADDR
*/

#define STDLIB_VER 1
#define STDLIB_SUBVER 0

#define VIDEO_MEMORY_START 0xF060

#define JMPADDR 0xFF
#define VIDEO_CARET 0xF0

; Imidiate operations

#macro ADDi(src, imd, str) {
    LDI 0xE0, imd
    ADD src, 0xE0, str
}

#macro SUBi(src, imd, str) {
    LDI 0xE0, imd
    SUB src, 0xE0, str
}

#macro MULi(src, imd, str) {
    LDI 0xE0, imd
    MUL src, 0xE0, str
}

#macro DIVi(src, imd, str) {
    LDI 0xE0, imd
    DIV src, 0xE0, str
}

#macro MODi(src, imd, str) {
    LDI 0xE0, imd
    MOD src, 0xE0, str
}

#macro EQi(src, imd, str) {
    LDI 0xE0, imd
    EQ src, 0xE0, str
}

#macro GTi(src, imd, str) {
    LDI 0xE0, imd
    GT src, 0xE0, str
}

#macro LTi(src, imd, str) {
    LDI 0xE0, imd
    LT src, 0xE0, str
}

#macro INC(qmem, i) {
    ADDi qmem, i, qmem
}

#macro DEC(qmem, i) {
    SUBi qmem, i, qmem
}

; INIT

LDI VIDEO_CARET, VIDEO_MEMORY_START

JMP main

; HALT

#macro HALT() {
    JMP __halt
}

__halt:
    JMP .loop
.loop:
    JMP JMPADDR

; Library Functions

/*
    stdlib_jump_cursor
    Args
        0xA0 - Position
    Return
        NONE        
*/

stdlib_jump_cursor:
    MOV 0xA0, VIDEO_CARET
    RET

/*
    stdlib_putc
    Args
        0xA0 - Character
        0xA1 - Style
    Return
        NONE
*/

stdlib_putc:
    LDI 0x00, '\n'
    EQ 0xA0, 0x00, 0x00
    JIF .new_line, 0x00
    LDI 0x00, '\t'
    EQ 0xA0, 0x00, 0x00
    JIF .tabulator, 0x00
    JMP .normal_character
.new_line:
    DEC VIDEO_CARET, VIDEO_MEMORY_START
    DIVi VIDEO_CARET, (80*2), VIDEO_CARET
    INC VIDEO_CARET, 1
    MULi VIDEO_CARET, (80*2), VIDEO_CARET
    INC VIDEO_CARET, VIDEO_MEMORY_START
    JMP .end
.tabulator:
    DEC VIDEO_CARET, VIDEO_MEMORY_START
    DIVi VIDEO_CARET, (4*2), VIDEO_CARET
    INC VIDEO_CARET, 1
    MULi VIDEO_CARET, (4*2), VIDEO_CARET
    INC VIDEO_CARET, VIDEO_MEMORY_START
    JMP .end
.normal_character:
    STP 0xA0, VIDEO_CARET
    INC VIDEO_CARET, 1
    STP 0xA1, VIDEO_CARET
    INC VIDEO_CARET, 1
.end:
    RET

/*
    stdlib_puts
    Args
        0xA0 - String Pointer
        0xA1 - Style
    Return
        NONE
*/

stdlib_puts:
    MOV 0xA0, 0x08 ; Copy over the string pointer
.loop:
    LDP 0x09, 0x08 ; Load a string character
    LDI 0x0A, 0 ; Load a constant for null terminator check

    EQ 0x0A, 0x09, 0x0A ; Compare char with '\0'
    JIF .end, 0x0A

    MOV 0x09, 0xA0 ; Move current character into arg for putc
    ; 0xA1 is already Style
    CALL stdlib_putc

    INC 0x08, 1

    JMP .loop
.end:
    RET

/*
    stdlib_clear
    Args
        NONE
    Return
        NONE
*/
stdlib_clear:
    LDI 0x08, 0 ; Counter
.loop:
    ADDi 0x08, VIDEO_MEMORY_START, 0x09
    LDI 0x0A, 0x00
    STP 0x0A, 0x09

    EQi 0x08, 4000, 0x09
    JIF .end, 0x09

    INC 0x08, 1
    JMP .loop
.end:
    LDI VIDEO_CARET, VIDEO_MEMORY_START
    RET
