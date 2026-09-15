# You will be using this file to write your own program. 
# You will have access to the internet during this portion, with the exception of Artificial Intelligence.

# You have 30 minutes.
# Step 1: Research
# Step 2: Plan
# Step 3: Code
# Step 4: Debug
- Takeoff into the air
- Wait 10 seconds
- Fly forwards for 10 meters at 5 m/s
- Return to launch (including landing)

#Have the drone connect to the computer and then takeoff, 
class Drone(asyncio): 
    def __init__(self, port = "udpin://0.0.0.0:14540"):
        self.drone = System()
        self.port = "udpin://0.0.0.0:14540"

    async def connect(self): 
        connected = False

        await self.drone.connect(system_address=self.port)
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                break
await asyncio.sleep(10)
def takeoff(self, alt) 
        await self.drone.action.arm()
        await self.drone.action.set_takeoff_altitude(alt 10 meters at 5 meters/seconds)
altitude = 0
while set_takeoff_altitude > 0:
    print(starting flight)
    count += 1
Altitude meters = [2 meters/seconds]
leave launchpad
        await self.drone.action.takeoff()
async def land(self):
        try?:
            await self.drone.offboard.stop()
        except Exception: 
            pass

        await self.drone.action.land()
return to launchpad

#Priscilla To priscillapriscilla5020@gmail.com