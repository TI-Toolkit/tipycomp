#!/usr/bin/env python3

import os
import subprocess
import sys
import tempfile


DISASSEMBLER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mpy-disasm", "mpy-disasm")


class FormatError(ValueError):
    pass


def get_menu_pos(data):
    if not data.startswith(b"PYMP"):
        raise FormatError("payload does not start with PYMP")

    length = 0
    index = 4
    shift = 0
    while True:
        if index >= len(data):
            raise FormatError("truncated menu length")
        byte = data[index]
        length |= (byte & 0x7f) << shift
        index += 1
        shift += 7
        if byte & 0x80 == 0:
            break
        if shift >= 35:
            raise FormatError("menu length is too large")

    if index >= len(data):
        raise FormatError("missing PYMP format version")
    if data[index] != 2:
        raise FormatError("unsupported PYMP format version {}".format(data[index]))

    start = index + 1
    end = start + length
    if end > len(data):
        raise FormatError("menu extends beyond the payload")
    if length == 0 or data[end - 1] != 0:
        raise FormatError("menu is not NUL-terminated")
    return start, end


def split_payload(data):
    start, end = get_menu_pos(data)
    mpy_data = data[end:]
    if len(mpy_data) < 4 or mpy_data[0] != ord("M"):
        raise FormatError("payload does not contain .mpy bytecode")
    return data[start:end - 1], mpy_data


def dump_menu(data, outfile=None):
    menu, _ = split_payload(data)
    if outfile:
        with open(outfile, "wb") as output:
            output.write(menu)
    else:
        print(str(menu, encoding="utf8"))


def disasm(data, temp_dir):
    _, mpy_data = split_payload(data)
    mpy_filename = temp_dir + "/in.mpy"
    with open(mpy_filename, "wb") as output:
        output.write(mpy_data)
    subprocess.run([DISASSEMBLER, mpy_filename], check=True)


def main(mode, infile, outfile=None):
    valid = (mode == "menu" or
             (mode == "disasm" and outfile is None) or
             (mode == "extract" and outfile is not None))
    if not valid:
        print("Invalid arguments")
        print("Use 'menu' or 'disasm' with an input file, or 'extract' with input and output files")
        return 1

    temp_dir = tempfile.TemporaryDirectory(prefix="tipycomp_")
    bin_filename = temp_dir.name + "/in.bin"

    subprocess.run(["convbin",
                    "-i", infile, "-j", "8x",
                    "-o", bin_filename, "-k", "bin"],
                   check=True, stdout=subprocess.DEVNULL)

    with open(bin_filename, "rb") as bin_file:
        data = bin_file.read()

    if mode == "menu":
        dump_menu(data, outfile)
    elif mode == "disasm":
        disasm(data, temp_dir.name)
    else:
        _, mpy_data = split_payload(data)
        with open(outfile, "wb") as output:
            output.write(mpy_data)
    return 0


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print("Usage: " + __file__ + " (menu|disasm) infile [outfile.menu]")
        print("       " + __file__ + " extract infile outfile.mpy")
        sys.exit(1)
    try:
        sys.exit(main(*sys.argv[1:]))
    except (FormatError, OSError, subprocess.CalledProcessError) as error:
        print("tipydecomp: {}".format(error), file=sys.stderr)
        sys.exit(1)
