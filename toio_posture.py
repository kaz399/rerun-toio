#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from logging import getLogger

import rerun as rr
import rerun.blueprint as rrb
from scipy.spatial.transform import Rotation as R
from toio.cube import (
    PostureAngleDetectionCondition,
    PostureAngleDetectionType,
    PostureAngleQuaternionsData,
    Sensor,
    ToioCoreCube,
)

logger = getLogger(__name__)


async def log_quaternion_posture():
    count: int = 0

    def sensor_handler(payload: bytearray):
        sensor_info = Sensor.is_my_data(payload)
        if isinstance(sensor_info, PostureAngleQuaternionsData):
            x, y, z, w = sensor_info.x, sensor_info.y, sensor_info.z, sensor_info.w
            logger.info("x:%f y:%f z:%f w:%f", x, y, z, w)
            posture = R.from_quat([x, y, z, w])
            rr.log(
                "world/toio",
                rr.InstancePoses3D(quaternions=rr.Quaternion(xyzw=posture.as_quat())),
            )
            nonlocal count
            count += 1

    async with ToioCoreCube() as cube:
        await cube.api.configuration.set_posture_angle_detection(
            PostureAngleDetectionType.Quaternions,
            50,
            PostureAngleDetectionCondition.Always,
        )
        await cube.api.sensor.register_notification_handler(sensor_handler)
        while count < 200:
            await asyncio.sleep(0.1)
        await cube.api.sensor.unregister_notification_handler(sensor_handler)


def setup():
    rr.init("toio posture viewer", spawn=True)

    rr.reset_time()
    rr.log("world", rr.ViewCoordinates.RIGHT_HAND_Z_DOWN, static=True)

    colors = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    vectors = [[0.1, 0.0, 0.0], [0.0, 0.1, 0.0], [0.0, 0.0, 0.1]]
    origins = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    labels = ["X", "Y", "Z"]
    rr.log(
        "world/axis",
        rr.Arrows3D(origins=origins, vectors=vectors, colors=colors, labels=labels),
    )
    rr.log("world/toio", rr.Asset3D(path="./assets/toiocorecube_v003.gltf"))
    rr.send_blueprint(rrb.Spatial3DView(origin="/world"))


async def main():
    setup()
    await log_quaternion_posture()
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
