# tipycomp

A tool for compiling Python modules for the TI-83 Premium CE EP / TI-84 Plus CE-T Python Edition.

### Installation

You will need [convbin](https://github.com/mateoconlechuga/convbin). If you have the CE toolchain installed, you most likely already have this tool.

You will also need version 1.9.3 specifically of the [mpy-cross](https://pypi.org/project/mpy-cross/) module. You can install it using `pip install -Iv mpy_cross==1.9.3`.

To use the disassembly mode of tipydecomp, you will need to build mpy-disasm by running `make` in its directory. 

### Usage

#### tipycomp

```
python tipycomp.py pyfile menufile outfile varname (mpy-cross args)
```
where `pyfile` is the Python file to compile, `menufile` is a text file containing menu definitions, `outfile` is the output 8xv, and `varname` is the name of the appvar.
You may also optionally pass additional arguments to mpy-cross by adding them after the other four arguments.

To use the module, send it to the calculator using TI-Connect CE. In the Python editor, add the line `from varname import *`, where `varname` is the name of the appvar. You can then see the module's menu by pressing "math" and selecting it from the modules list.

#### tipydecomp
```
python tipydecomp.py menu infile.8xv [outfile.menu]
```
to dump the menu definitions of `infile.8xv`, or write the exact menu bytes to `outfile.menu`.

```
python tipydecomp.py disasm infile.8xv
```
to disassemble the MicroPython bytecode of `infile.8xv`.

```
python tipydecomp.py extract infile.8xv outfile.mpy
```
to extract the original version-3 `.mpy` payload.

### Menu file format
The menu definitions file is a plain text file containing the menu structure for the module. It consists of a series of directives, one per line. All official TI modules use Unix-style line endings, although Windows-style line endings also appear to work.

There are four kinds of directive:
- `#MENULABEL (text)` - Displays an option containing `(text)` in the Modules menu, which can be opened by pressing "math." When clicked, it will open a menu that is defined by all directives following this one but before the next `#MENULABEL` directive.
- `#MENUTITLE (text)` - Sets the title of the first page of the menu to `(text)`.
- `#MENUTOP (text)` - Adds a new page to the menu with a title of `(text)`. Pages can be switched between using the left and right arrow keys.
- `#MENUITEM (display)|(insert)|(offset)` - Adds a menu option to the page defined by the previous `#MENUTITLE` or `#MENUTOP` directive. In the menu, the text `(display)` will be shown. When clicked, it will insert the text `(insert)`. `(offset)` is the number of characters before the end of the inserted text to place the cursor. `|(offset)` can be omitted if the cursor is placed at the end of the insertion.

The following special characters may be used in menu text:
```
<%TAB%>
<%NL%>
<%ELLIPSIS%>
<%LEFT_ARROW_HEAD%>
<%RIGHT_ARROW_HEAD%>
<%UP_ARROW_HEAD%>
<%DOWN_ARROW_HEAD%>
<%ANGLE%>
<%EXCLAM_INVERTED%>
<%CENT_SIGN%>
<%POUND_SIGN%>
<%CURRENCY_SIGN%>
<%YEN_SIGN%>
<%BROKEN_BAR%>
<%SECTION_SIGN%>
<%COPYRIGHT_SIGN%>
<%FEMININE_ORDINAL%>
<%LEFT_DOUBLE_ANGLE%>
<%NOT_SIGN%>
<%REGISTERED_SIGN%>
<%DEGREE_SIGN%>
<%PLUS_MINUS%>
<%SUPERSCRIPT_TWO%>
<%SUPERSCRIPT_THREE%>
<%MICRO_SIGN%>
<%PILCROW_SIGN%>
<%MIDDLE_DOT%>
<%SUPERSCRIPT_ONE%>
<%MASCULINE_ORDINAL%>
<%RIGHT_DOUBLE_ANGLE%>
<%FRACTION_ONE_QUARTER%>
<%FRACTION_ONE_HALF%>
<%FRACTION_THREE_QUARTERS%>
<%INVERTED_QUESTION_MARK%>
<%CAP_A_GRAVE%>
<%CAP_A_ACUTE%>
<%CAP_A_CIRCUMFLEX%>
<%CAP_A_TILDE%>
<%CAP_A_DIAERESIS%>
<%CAP_A_RING%>
<%CAP_AE%>
<%CAP_C_CEDILLA%>
<%CAP_E_GRAVE%>
<%CAP_E_ACUTE%>
<%CAP_E_CIRCUMFLEX%>
<%CAP_E_DIAERESIS%>
<%CAP_I_GRAVE%>
<%CAP_I_ACUTE%>
<%CAP_I_CIRCUMFLEX%>
<%CAP_I_DIAERESIS%>
<%CAP_ETH%>
<%CAP_N_TILDE%>
<%CAP_O_GRAVE%>
<%CAP_O_ACUTE%>
<%CAP_O_CIRCUMFLEX%>
<%CAP_O_TILDE%>
<%CAP_O_DIAERESIS%>
<%MULTIPLY%>
<%CAP_O_STROKE%>
<%CAP_U_GRAVE%>
<%CAP_U_ACUTE%>
<%CAP_U_CIRCUMFLEX%>
<%CAP_U_DIAERESIS%>
<%CAP_Y_ACUTE%>
<%CAP_THORN%>
<%SHARP_S%>
<%A_GRAVE%>
<%A_ACUTE%>
<%A_CIRCUMFLEX%>
<%A_TILDE%>
<%A_DIAERESIS%>
<%A_RING%>
<%AE%>
<%C_CEDILLA%>
<%E_GRAVE%>
<%E_ACUTE%>
<%E_CIRCUMFLEX%>
<%E_DIAERESIS%>
<%I_GRAVE%>
<%I_ACUTE%>
<%I_CIRCUMFLEX%>
<%I_DIAERESIS%>
<%ETH%>
<%N_TILDE%>
<%O_GRAVE%>
<%O_ACUTE%>
<%O_CIRCUMFLEX%>
<%O_TILDE%>
<%O_DIAERESIS%>
<%DIVIDE%>
<%O_STROKE%>
<%U_GRAVE%>
<%U_ACUTE%>
<%U_CIRCUMFLEX%>
<%U_DIAERESIS%>
<%Y_ACUTE%>
<%THORN%>
<%Y_DIAERESIS%>
```

The following color codes can be used in menu text:
```
<@BLACK@>
<@BLUE@>
<@GREEN@>
<@CYAN@>
<@RED@>
<@MAGENTA@>
<@YELLOW@>
<@GRAY@>
<@WHITE@>
```

Example:
```
#MENULABEL my_module<%ELLIPSIS%>
#MENUTITLE my_module
#MENUITEM myfunc(<@BLUE@>num<@BLACK@>)|myfunc()|1
```
