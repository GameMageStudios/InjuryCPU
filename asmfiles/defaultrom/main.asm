#include "../stdlib.asm"

#macro m_display_color(character, color) {
    LDI 0xA0, character
    LDI 0xA1, color
    CALL stdlib_putc
    LDI 0xA0, 0x20 ; Space
    CALL stdlib_putc
    CALL stdlib_putc
    CALL stdlib_putc
}

MSG1:
    .db "INJURY CPU\n"
    .db "-\tSimulator made in Scratch, Assembler made in Python 3.13\n"
    .db "\n"
    .db "Supports 16 Colors\n"
    .db "Light Colors:\t"
    .db 0x00
MSG2:
    .db "\nDark Colors:\t"
    .db 0x00
MSG3:
    .db "\n\n"
    .db "The CPU can use:\n"
    .db "\t256 x 16-bit : Quick Memory (Basicaly 256 registers)\n"
    .db "\t65536 x 8-bit : RAM\n"
    .db "\t80x25 16-color character display\n"
    .db "\n"
    .db "You might have inputed an invalid ROM (length % 2 == 1), an empty ROM\n"
    .db "or no ROM, this is the ROM default fallback.\n"
    .db "\n"
    .db "CREDITS\n"
    .db "\tDisplay Font: GameMageStudios\n"
    .db "\tScratch Code: GameMageStudios\n"
    .db "\tDefault ROM: GameMageStudios\n"
    .db "\n"
    .db "For more info on this project, visit\n\t"
    .db 0x00
MSG4:
    .db "https://gamemagestudios.github.io/InjuryCPU/\n"
    .db 0x00
MSG5:
    .db "\n"
    .db "PRESS ANY KEY..."
    .db 0x00

main_func:
    c_STDLIB_PLAY_TONE 80, 5
    c_STDLIB_PLAY_TONE 78, 5
    c_STDLIB_PLAY_TONE 86, 25

    c_STDLIB_PUTS MSG1, 0x10

    m_display_color '0', 0x80
    m_display_color '1', 0x91
    m_display_color '2', 0xA2
    m_display_color '3', 0xB3
    m_display_color '4', 0xC4
    m_display_color '5', 0xD5
    m_display_color '6', 0xE6
    m_display_color '7', 0xF7

    c_STDLIB_PUTS MSG2, 0x10

    m_display_color '8', 0x08
    m_display_color '9', 0x19
    m_display_color 'A', 0x2A
    m_display_color 'B', 0x3B
    m_display_color 'C', 0x4C
    m_display_color 'D', 0x5D
    m_display_color 'E', 0x6E
    m_display_color 'F', 0x7F

    c_STDLIB_PUTS MSG3, 0x10

    c_STDLIB_PUTS MSG4, 0x60

    c_STDLIB_PUTS MSG5, 0x10

    RET

main:
    CALL main_func

.loop:
    INP 0x10
    EQi 0x10, 0x00, 0x10

    JIN .key_pressed, 0x10

    JMP .loop
.key_pressed:
    CALL stdlib_clear
    CALL main_func
    JMP .loop
