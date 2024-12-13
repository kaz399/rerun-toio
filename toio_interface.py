import asyncio
from dataclasses import dataclass
from logging import getLogger

from toio.cube import (
    PostureAngleDetectionCondition,
    PostureAngleDetectionType,
    ToioCoreCube,
)
from toio.cube.api.button import Button, ButtonInformation, ButtonState
from toio.cube.api.sensor import (
    PostureAngleQuaternionsData,
    Sensor,
)

import rerun as rr
from scipy.spatial.transform import Rotation as R

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

    async def sensor_handler(payload: bytearray):
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
