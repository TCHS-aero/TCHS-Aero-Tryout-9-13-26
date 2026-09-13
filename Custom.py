#!/usr/bin/env python3

"""
Caveat when attempting to run the examples in non-gps environments:

`drone.offboard.stop()` will return a `COMMAND_DENIED` result because it
requires a mode switch to HOLD, something that is currently not supported in a
non-gps environment.
"""

import asyncio
import logging

from mavsdk import System
from mavsdk.offboard import OffboardError, PositionNedYaw

# Enable INFO level logging by default so that INFO messages are shown
logging.basicConfig(level=logging.INFO)


async def run():
    """Does Offboard control using position NED coordinates."""

    drone = System()
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Setting initial setpoint")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))

    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(
            f"Starting offboard mode failed \
                with error code: {error._result.result}"
        )
        print("-- Disarming")
        await drone.action.disarm()
        return

    print(
        "-- GO 5m up"
    )
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 5.0, 0.0))
    await asyncio.sleep(10)

    print(
        "-- Go 10m North, \
            within local coordinate system"
    )
    await drone.offboard.set_position_ned(PositionNedYaw(10.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(1)

    await drone.offboard.set_position_ned(PositionNedYaw(-10.0, 0.0, 0.0, 0.0))
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -5.0, 0.0))

    print("-- Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(
            f"Stopping offboard mode failed \
                with error code: {error._result.result}"
        )


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())

    # John Diep jdiep6281@tcusd.net
    # Dextere Du ddu1421@tcusd.net
    # Ethan Wu ewu3854@tcusd.net