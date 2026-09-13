# You will be using this file to write your own program. 
# You will have access to the internet during this portion, with the exception of Artificial Intelligence.

# You have 30 minutes.
# Step 1: Research
# Step 2: Plan
# Step 3: Code
# Step 4: Debug

import asyncio
from mavsdk import System

async def main():
    drone_object = System("udpin://0.0.0.0:14540")
    await drone_object.connect()
    await drone_object.action.arm()
    await drone_object.action.takeoff()
    await drone_object.offboard.set_velocity_ned(0.0, 0.0, 0.0, 0.0)
    await drone_object.move("forwards", 10, 50)
    await drone_object.action.return_to_launch()
    await drone_object.action.land()

if __name__ == "__main__":
    asyncio.run(main)

# Zacheus Wu - ewu2055@tcusd.net