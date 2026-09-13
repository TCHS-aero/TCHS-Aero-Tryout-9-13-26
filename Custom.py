# You will be using this file to write your own program. 
# You will have access to the internet during this portion, with the exception of Artificial Intelligence.

# You have 30 minutes.
# Step 1: Research
# Step 2: Plan
# Step 3: Code
# Step 4: Debug

import asyncio
from mavsdk import System
from mavsdk.offboard import VelocityNedYaw


async def main():
    drone = System()
    await drone.connect(
        system_address="udpin://0.0.0.0:14540"
    )
    async for state in drone.core.connection_state():
        if state.is connected:
            break
    async for health in drone.telemetry .health():
        if(
            health.is_global_position_ok and health.is_home_position_ok
        ):
        break
    await drone.action.set_takeoff_altitude(5)
    await drone.action.arm()
    try:
        await drone.action.takeoff()
        await async.sleep(10)
        







    



if __name__ == "__main__":
    asyncio.run(main)
