#!/usr/bin/env python3

import os
import subprocess
import sys
import tempfile


DISASSEMBLER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mpy-disasm", "mpy-disasm")


class FormatError(ValueError):
    pass


def read_record_length(data, index):
    length = 0
    for shift in range(0, 35, 7):
        if index >= len(data):
            raise FormatError("truncated record length or missing record-stream terminator")
        byte = data[index]
        if shift == 28 and byte & 0xf0:
            raise FormatError("record length is too large")
        length |= (byte & 0x7f) << shift
        index += 1
        if byte & 0x80 == 0:
            return length, index


def split_payload(data):
    if not data.startswith(b"PYMP"):
        raise FormatError("payload does not start with PYMP")

    menus = []
    index = 4
    while True:
        length, index = read_record_length(data, index)
        if length == 0:
            break
        end = index + length
        if end > len(data):
            raise FormatError("record extends beyond the payload")
        # PYMP uses the same record stream as PYCD/PYSC. Length includes
        # the record ID: 1 is a filename, 2 is menu definitions.
        if data[index] == 2:
            menus.append(data[index + 1:end])
        index = end

    mpy_data = data[index:]
    if len(mpy_data) < 4 or mpy_data[0] != ord("M"):
        raise FormatError("payload does not contain .mpy bytecode")
    return b"".join(menus), mpy_data


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
