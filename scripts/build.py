#! /usr/bin/env python3
import os
import shutil

_TOP = ".."
SRC = os.path.join(_TOP, "src")
LIB = os.path.join(_TOP, "lib")
BUILD = os.path.join(_TOP, "build")

def copy_contents(frm, to):
    for f in os.listdir(frm):
        print("Copying file '{}' from '{}' to '{}'".format(f, frm, to))
        shutil.copyfile(os.path.join(frm, f), os.path.join(to, f))

if __name__ == "__main__":
    if not os.path.isdir(BUILD):
        print("Generating bin folder")
        os.mkdir(BUILD)
    else:
        print("Clearing bin folder")
        for f in os.listdir(BUILD):
            os.remove(os.path.join(BUILD, f))

    copy_contents(SRC, BUILD)
    copy_contents(LIB, BUILD)
