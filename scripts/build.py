#! /usr/bin/env python3
import os
import shutil

import sys
sys.path.append("..")
import tests

# begin unittesting
result = tests.test_source()
if not result.wasSuccessful():
    print("tests failed, aborting build")
    exit(1)

_TOP = ".."
SRC = os.path.join(_TOP, "src")
LIB = os.path.join(_TOP, "lib")
BUILD = os.path.join(_TOP, "build")


def copy_contents(frm, to):
    for f in os.listdir(frm):
        from_f = os.path.join(frm, f)
        if os.path.isfile(from_f):
            print("Copying file '{}' from '{}' to '{}'".format(f, frm, to))
            shutil.copyfile(from_f, os.path.join(to, f))


if __name__ == "__main__":
    if not os.path.isdir(BUILD):
        print("Generating build folder")
        os.mkdir(BUILD)
    else:
        print("Clearing build folder")
        for f in os.listdir(BUILD):
            os.remove(os.path.join(BUILD, f))

    copy_contents(SRC, BUILD)
    copy_contents(LIB, BUILD)
