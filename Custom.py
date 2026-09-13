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
    drone = System("udpin://0.0.0.0:14540")
    await drone.connect()
    await drone.action.arm()
    await drone.action.takeoff(10)

    await asyncio.sleep(10)

    await drone.offboard.set_position_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    
    await drone.offboard.start()
    await drone.offboard.set_velocity_ned(VelocityNedYaw(5.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(2)
    await drone.return_to_launch()

if __name__ == "__main__":
    asyncio.run(main)

#Zonglei Sun (lemmonboys99@gmail.com)