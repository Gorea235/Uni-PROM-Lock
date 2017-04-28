#! /usr/bin/env python3
import os
import shutil

_TOP = ".."
SRC = os.path.join(_TOP, "src")
LIB = os.path.join(_TOP, "lib")
BIN = os.path.join(_TOP, "bin")

def copy_contents(frm, to):
    for f in os.listdir(frm):
        print("Copying file '{}' from '{}' to '{}'".format(f, frm, to))
        shutil.copyfile(os.path.join(frm, f), os.path.join(to, f))

if __name__ == "__main__":
    if not os.path.isdir(BIN):
        print("Generating bin folder")
        os.mkdir(BIN)
    else:
        print("Clearing bin folder")
        for f in os.listdir(BIN):
            os.remove(os.path.join(BIN, f))

    copy_contents(SRC, BIN)
    copy_contents(LIB, BIN)
