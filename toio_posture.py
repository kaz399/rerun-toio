#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from logging import getLogger

import rerun as rr
from scipy.spatial.transform import Rotation as R
from toio.cube import (
    Button,
    ButtonInformation,
    ButtonState,
    PostureAngleDetectionCondition,
    PostureAngleDetectionType,
    PostureAngleQuaternionsData,
    Sensor,
    ToioCoreCube,
)

logger = getLogger(__name__)


@dataclass
class ToioButton:
    pressed: bool = False


async def toio_quaternion():
    button_state = ToioButton()

    def button_handler(payload: bytearray):
        button = Button.is_my_data(payload)
        if isinstance(button, ButtonInformation):
            nonlocal button_state
            logger.info("** BUTTON STATE: %s", ButtonState(button.state).name)
            if button.state == ButtonState.PRESSED and not button_state.pressed:
                button_state.pressed = True

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

    async with ToioCoreCube() as cube:
        await cube.api.configuration.set_posture_angle_detection(
            PostureAngleDetectionType.Quaternions,
            50,
            PostureAngleDetectionCondition.Always,
        )
        await cube.api.sensor.register_notification_handler(sensor_handler)
        await cube.api.button.register_notification_handler(button_handler)
        while not button_state.pressed:
            await asyncio.sleep(0.1)
        await cube.api.button.unregister_notification_handler(button_handler)
        await cube.api.sensor.unregister_notification_handler(sensor_handler)
        logger.info("** DISCONNECTING")
    logger.info("** DISCONNECTED")


def setup():
    rr.init("toio_posture_viewer", spawn=True)

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


async def main():
    setup()
    await toio_quaternion()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
