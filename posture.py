#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     posture.py
#
#     Copyright 2024 YABE Kazuhiro
#
# ************************************************************

from __future__ import annotations

import argparse
import fileinput
import sys
from logging import (
    DEBUG,
    INFO,
    NOTSET,
    WARNING,
    basicConfig,
    Filter,
    Formatter,
    Handler,
    NullHandler,
    StreamHandler,
    getLogger,
)

import rerun as rr

logger = getLogger(__name__)
if __name__ == "__main__":
    default_log_level = DEBUG
    handler: Handler = StreamHandler()
    handler.setLevel(default_log_level)
    formatter = Formatter("%(asctime)s %(levelname)7s [%(name)s] %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(default_log_level)
else:
    default_log_level = NOTSET
    handler = NullHandler()

class MyLoggerFilter(Filter):
    def filter(self, record):
        if record.name == "xxx":
            return False
        return True

handler.addFilter(MyLoggerFilter())
basicConfig(
    handlers=[handler],
    level=default_log_level
)

def init_rerun(model_filename: str):
   rr.init("toio posture", spawn=True)

   rr.log("world", rr.ViewCoordinates.RIGHT_HAND_Z_DOWN, static=True)
   origins = [
       [0.0, 0.0, 0.0],
       [0.0, 0.0, 0.0],
       [0.0, 0.0, 0.0],
   ]
   vectors = [
       [0.1, 0.0, 0.0],
       [0.0, 0.1, 0.0],
       [0.0, 0.0, 0.1],
   ]
   colors = [
       [1.0, 0.0, 0.0],
       [0.0, 1.0, 0.0],
       [0.0, 0.0, 1.0],
   ]
   labels = ["X", "Y", "Z"]
   rr.log("world/axis", rr.Arrows3D(origins=origins, vectors=vectors, colors=colors, labels=labels))
   rr.log("world/toio", rr.Asset3D(path=model_filename))


def options(argv):
    op = argparse.ArgumentParser()
    op.add_argument("--dry-run", action="store_true", help="do not perform actions")
    op.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    op.add_argument("-q", "--quiet", action="store_true", help="quiet mode")
    op.add_argument("argv", nargs="*", help="args")
    opt = op.parse_args(argv[1:])
    # set logging level
    if opt.quiet:
        loglevel = WARNING
    elif opt.verbose:
        loglevel = DEBUG
    else:
        loglevel = INFO
    handler.setLevel(loglevel)
    logger.setLevel(loglevel)
    return opt


def main(argv):
    opt = options(argv)

    if len(opt.argv):
        init_rerun(opt.argv[0])
    else:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

