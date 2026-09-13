# You will be using this file to write your own program. 
# You will have access to the internet during this portion, with the exception of Artificial Intelligence.

# You have 30 minutes.
# Step 1: Research
# Step 2: Plan
# Step 3: Code
# Step 4: Debug 

# TAKEOFF INTO THE AIR
# Wait 10 seconds
# Fly forwards for 10 meters at 5 m/s
# Return to launch (including landing)

import asyncio
from mavsdk import System

async def main():
    drone = System("udpin://0.0.0.0:14540")
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()

    print("-- We are waiting for 10 seconds")
    await drone.action.hold()
    await asyncio.sleep(10)

    print("-- We are moving north at 5 m/s")
    await drone.offboard.AccelerationNed(5, 0, 0)

    print("-- Landing")
    await drone.offboard.AccelerationNed(0, 0, 0)
    await drone.action.return_to_launch()

    print("-- Disarming")
    await drone.action.disarm()

if __name__ == "__main__":
    asyncio.run(main)

# Dustin Kim dkim5042@tcusd.net, 
# Julien Tang julien24tang@gmail.com, 
# Brian Wong wongbrian313@gmail.com