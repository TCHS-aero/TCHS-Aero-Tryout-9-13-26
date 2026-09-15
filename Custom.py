import asyncio
from mavsdk import System
from mavsdk.offboard import OffboardError, VelocityNedYaw
async def run():
    drone = System()
    await drone.connect(system_address="udpin://0.0.0.0:14540")
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            break
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            break
    await drone.action.arm()
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(
            f"Starting offboard mode failed with error code: {error._result.result}"
        )
        print("-- Disarming")
        await drone.action.disarm()
        return
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, -10.0, 0.0))
    await asyncio.sleep(4)

    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(10)

    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 5.0, 0.0, 90.0))
    await asyncio.sleep(2)

    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, -5.0, 0.0, 0.0))
    await asyncio.sleep(2)

    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 10.0, 0.0))
    await asyncio.sleep(4)


    await
    print("-- Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(
            f"Stopping offboard mode failed with error code: {error._result.result}"
        )


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())

    # Jayden Wong Jwong4002@tcusd.net