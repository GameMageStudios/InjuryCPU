# Injury CPU Assembly Documentation

## Instruction Documentation

This table does not include compiled argument length.

Opcode (Dec) | Opcode (Hex) | Name | Alias  | Arg1       | Arg2       | Arg3       | Description
------------ | ------------ | ---- | ------ | ---------- | ---------- | ---------- | -----------
0|`00`|No Operation|`NOP`|-|-|-|No-Operation
1|`01`|Load Imidiate|`LDI`|`Q-addr`|`Value`|-|Loads a constant value into quick memory
2|`02`|Load|`LD`|`Q-addr`|`RAM-addr`|-|Loads a value from RAM into quick memory
3|`03`|Load from Pointer|`LDP`|`Q-addr-str`|`Q-addr-pnt`|-|Loads a value like `LD`, but instead of using an imidiate address, uses a "pointer", from `Q-addr-pnt`
4|`04`|Store|`ST`|`Q-addr`|`RAM-addr`|-|Stores a value (from `Q-addr`) into RAM
5|`05`|Store at Pointer|`STP`|`Q-addr-str`|`Q-addr-pnt`|-|Stores a value like `ST`, but instead of using an imidiate address, uses a "pointer", from `Q-addr-pnt`
6|`06`|Move|`MOV`|`Q-addr-src`|`Q-addr-str`|-|Copies a value from `Q-addr-src` to `Q-addr-str`
7|`07`|-|-|-|-|-|-
8|`08`|Add|`ADD`|`Q-addr-a`|`Q-addr-b`|`Q-addr-str`|Adds values from `Q-addr-a` and `Q-addr-b` and stores the result into `Q-addr-str`
9|`09`|Subtract|`SUB`|`Q-addr-a`|`Q-addr-b`|`Q-addr-str`|Subtracts the value from `Q-addr-b` from the value in `Q-addr-a` and stores the result into `Q-addr-str`
10|`0a`|Multiply|`MUL`|`Q-addr-a`|`Q-addr-b`|`Q-addr-str`|Multiplies values from `Q-addr-a` and `Q-addr-b` and stores the result into `Q-addr-str`
11|`0b`|Divide|`SUB`|`Q-addr-a`|`Q-addr-b`|`Q-addr-str`|Divides the value from `Q-addr-a` by the value in `Q-addr-b` and stores the result into `Q-addr-str`
12|`0c`|Modulo (Reminder)|`MOD`|`Q-addr-a`|`Q-addr-b`|`Q-addr-str`|Gets the reminder when dividing the value from `Q-addr-a` by the value in `Q-addr-b` and stores the result into `Q-addr-str`
13|`0d`|Bitwise AND|`AND`|`Q-addr-a`|`Q-addr-b`|`Q-addr-str`|Bitwise operation on `Q-addr-a` and `Q-addr-b`, stored in `Q-addr-str`
14|`0e`|Bitwise OR|`OR`|`Q-addr-a`|`Q-addr-b`|`Q-addr-str`|Bitwise operation on `Q-addr-a` and `Q-addr-b`, stored in `Q-addr-str`
15|`0f`|Bitwise XOR|`XOR`|`Q-addr-a`|`Q-addr-b`|`Q-addr-str`|Bitwise operation on `Q-addr-a` and `Q-addr-b`, stored in `Q-addr-str`
16|`10`|Negate|`NEG`|`Q-addr-src`|`Q-addr-str`|-|Since there are no negative numbers, works like $str = 65536 - src$
17|`11`|Bitwise Invert|`INV`|`Q-addr-src`|`Q-addr-str`|-|Flips bits of `Q-addr-src` and stores it in `Q-addr-str`
18|`12`|Compare - Equals|`EQ`|`Q-addr-a`|`Q-addr-b`|`Q-addr-str`|Compare operation on `Q-addr-a` and `Q-addr-b` stores the result into `Q-addr-str`
19|`13`|Compare - Greater Than|`GT`|`Q-addr-a`|`Q-addr-b`|`Q-addr-str`|Compare operation on `Q-addr-a` and `Q-addr-b` stores the result into `Q-addr-str`
20|`14`|Compare - Lesser Than|`LT`|`Q-addr-a`|`Q-addr-b`|`Q-addr-str`|Compare operation on `Q-addr-a` and `Q-addr-b` stores the result into `Q-addr-str`
21 ... 31|`15` - `1f`|-|-|-|-|-|-
32|`20`|Copy Program Counter|`CPC`|`Q-addr`|-|-|Legacy instruction, copies the program counter into quick memory
33|`21`|Jump|`JMP`|`Q-addr`|-|-|Jumps to the pc in `Q-addr`
34|`22`|Jump If|`JIF`|`Q-addr-pc`|`Q-addr-cond`|-|Jumps to the pc in `Q-addr-pc`, only if `Q-addr-cond` is not `0x0000`
35|`23`|Jump If Not|`JIN`|`Q-addr-pc`|`Q-addr-cond`|-|Jumps to the pc in `Q-addr-pc`, only if `Q-addr-cond` is `0x0000`
36|`24`|Call|`CALL`|`Q-addr`|-|-|Jumps to the pc in `Q-addr`, and stores the return address to be returned to with `RET`, call stack size is basicaly unlimited, because it is another simulated memory unit
37|`25`|Return|`RET`|-|-|-|Pops the most top element of the call stack, and jump to the address in it
38 ... 39|`26` - `27`|-|-|-|-|-|-
40|`28`|Collect Input|`INP`|`Q-addr`|-|-|Collects the buffered ASCII input of the simulation, stores in `Q-addr`
41|`29`|Sound|`SND`|`Q-addr`|-|-|Plays a midi note where the high byte of the value in `Q-addr` is the duration in one-hundredths of a second (100 = 1 second), and the low byte is the note from `0` - `255`

In the usage of `JMP`, `JIF`, `JIN`, `CALL`, the first argument can be replaced with a label, and gets replaced with (in the usage of `JMP`)
```injury
JMP main ; Gets compiled to "LDI JMPADDR main\nJMP JMPADDR"

; For the usage of this replace feature, `JMPADDR` must be `#define`-d, to be a quick memory address at where the label will be stored

main:
    JMP main
```

## Video Memory

The video memory is located in RAM, at addresses `0xF060` - `0xFFFF`
Where each two bytes gets displayed as one character

```
[  BYTE ONE  ] [  BYTE TWO  ]
( Character  ) ( FG )  ( BG )
8 bits         4 bits  4 bits
```

Colors (The same for `FG` and `BG`):
Index Hex | Color Name | Color Hex
--------- | ---------- | ---------
`0` | Black | `#000`
`1` | White | `#fff`
`2` | Red | `#f00`
`3` | Green | `#0f0`
`4` | Blue | `#00f`
`5` | Yellow | `#ff0`
`6` | Cyan | `#0ff`
`7` | Magenta | `#f0f`
`8` | Dark Gray | `#333`
`9` | Light Gray | `#888`
`a` | Dark Red | `#800`
`b` | Dark Green | `#080`
`c` | Dark Blue | `#008`
`d` | Dark Yellow | `#880`
`e` | Dark Cyan | `#088`
`f` | Dark Magenta | `#808`

## Getting Started

### Preprocessing

#### `#define`

```injury
; #define ALIAS value

; For example the standard library, includes a STDLIB_VER define

#define STDLIB_VER 1
#define STDLIB_SUBVER 0

#define VIDEO_MEMORY_START 0xF060

#define JMPADDR 0xFF
#define VIDEO_CARET 0xF0
```

Anything you have `#define`-d can be accessed by the allias, being replaced by the value, before complilation.

#### `#macro`

```injury
/*
#macro NAME(arguments...) {
    body
}
*/
0
; One macro from the standard library

#macro ADDi(src, imd, str) {
    LDI 0xE0, imd
    ADD src, 0xE0, str
}

ADDi 0x00, 5, 0x01 ; Use like instruction
```

Similar to `#define`, each instance gets replaced with the macro body, with the arguments of the macro being replaced too.

#### `#include`

```injury
#include "stdlib.asm"
```

`#include` gets replaced with the file in the quotes.

#### `.db` and `.dw`

<!--- Add proper docs --->

```injury
.db "Hello world", 0x00 ; Adds bytes to the compiled output
.dw 0xF060, 0xA078 ; Adds words (16-bit values) to the compiled output
```

### Stardard Library

In the [github repository](https://github.com/GameMageStudios/InjuryCPU), the `asmfiles/` contains `stdlib.asm`, or the *Standard Library*.
This is the most important library you are propably going to use.
It contains video functions like `stdlib_puts` or `stdlib_clear` or usefull macros like `ADDi` (Add imidiate) or `DEC` (Decrement)

The standard library is mostly documented in the code, and `#include`-ing it requires following some quick memory rules, documented at the top of the file.

The standard library may be distributed with diferent versions, so a `#define` exists for `STDLIB_VER` - The main version, change meaning a huge change in the implementation or interface, and `STDLIB_SUBVER` - The patch/implementation version (A change in implementation would require a `STDLIB_VER` change, unless the method of calling and result is the same).

Current official versions:
`VER` | `SUBVER` | Description of change
----- | -------- | ----------------------------------
1     | 0        | The first implementation.
2     | 0        | Added the `stdlib_play_tone` function, as well as `c_STDLIB_*` macros for every function, enabeling quicker function calling with static parameters.
