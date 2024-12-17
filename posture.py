#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
import argparse
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

import toio_interface

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
basicConfig(handlers=[handler], level=default_log_level)


def init(model_filename: str):
    logger.info("load: %s", model_filename)
    #rr.init("toio_posture_viewer", spawn=True)
    rr.connect_tcp("192.168.1.38:9876")

    rr.reset_time()
    rr.log("world", rr.ViewCoordinates.RIGHT_HAND_Z_DOWN, static=True)
    rr.log("mat", rr.EncodedImage(path="./assets/toio_playmat.png"), static=True)

    colors = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    vectors = [[0.1, 0.0, 0.0], [0.0, 0.1, 0.0], [0.0, 0.0, 0.1]]
    origins = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    labels = ["X", "Y", "Z"]
    rr.log(
        "world/axis",
        rr.Arrows3D(origins=origins, vectors=vectors, colors=colors, labels=labels),
    )
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


async def main(argv):
    opt = options(argv)

    if len(opt.argv):
        init(opt.argv[0])
        await toio_interface.toio_quaternion()
    else:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv)))
