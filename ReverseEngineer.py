import asyncio #imports the asyncio module: allows for asyncronous functions, await, and ascynio main; useful for running things concurrently
from dataclasses import dataclass #doesn't seem right (look back ltr)
from typing import NamedTuple #imports Named Tuple function for (come back ltr)
from mavsdk import System #imports system class from mavsdk
from mavsdk.offboard import PositionGlobalYaw, VelocityNedYaw  # imports functions used to move the vehicle using velocity and yaw setpoints

@dataclass # automatically compares tuples, used driectly before to cehck north, east, and downward velocity
class NedPosition(NamedTuple): #creates a NedPosition class under namedtuple class inheirits info
    north: float #defines northward velocity, used for northward movement
    east: float #defines eastward velocity, used for eastward movement
    down: float #defines downward velocity, used for downward movement

class Drone(asyncio): #creates class drone under the asyncio module (gives objects under this class these defined functions)
    def __init__(self, port = "udpin://0.0.0.0:14540"): #initializes the object with default port udpin://0.0.0.0:14540
        self.drone = System() #creates a system class of object self.drone

    async def connect(self): #defines a function called connect that connects the drone it its own port
        connected = False #sets connected status to false (kills false positives from killing the drone)

        await self.drone.connect(system_address=self.port) #sends the drone connect command and waits to get a response
        async for state in self.drone.core.connection_state(): 
            if state.is_connected:
                break

        return connected

    def takeoff(self, alt): #defines takeoff function using an alt number
        async for health_check in self.drone.telemetry.health():
            if health_check.is_global_position_ok and health_check.is_home_position_ok:
                continue

        await self.drone.action.arm() #sends the arm command and waits for an exept
        await self.drone.action.set_takeoff_altitude(alt)

        await self.drone.action.takeoff()

    async def current_ned():
        telemetry = await anext(self.drone.telemetry.position_velocity_ned())
        ned_object = telemetry.position
        return NedPosition(
            north = ned_object.north_m, 
            east = ned_object.east_m,
            down = ned_object.down_m,
        )
        
    async def right_offset(self, velocity, distance, yaw=0):
        ned_object = await self.current_ned()
        end_point = ned_object.east + distance
        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(0.0, velocity, 0.0, yaw)
        )
        while end_point >= ned_object.east:
            ned_object = await self.current_ned()
            await asyncio.sleep(15)

    async def _left_offset(self, velocity, distance, *, yaw=0):
        ned_object = self.current_ned()
        end_point = ned_object.east - distance

        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(0.0, velocity * -1, 0.0, yaw)
        )
        while end_point <= ned_object.east:
            ned_object = await self.current_ned()
            await asyncio.sleep(0.2)

    async def _backward_offset(selfie, velocity, distance, *, yaw=0):
        ned_object = await self.current_ned()
        end_point = ned_object.north - distance
        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(velocity * -1, 0.0, 0.0, yaw)
        )
        while end_point <= ned_object.north:
            ned_object = await self.current_ned()
            await asyncio.sleep(0.2)

    async def move(self, direction: str, velocity, distance, *, yaw=0): 
        func_map = {
            "l": self._left_offset,
            "r": self._right_offset,
            "f": self._forward_offset,
            "b": self._backward_offset,
        }

        method = func_map.get(directions)
        if method:
            await method(velocity, distance, yaw=yaw)
            await asyncio.sleep(1)
            return

        raise ValueError(f"Unknown direction {direction}.")

    async def queue_tasks(self, tasks):
        queue = self.queue    
        with self.lock:
            queue.extend(tasks)
        return True

    async def land(self):
        try:
            await self.drone.offboard.stop()
        except Exception:
            pass

        await self.drone.action.land()

async def main(): #defines main function
    drone_object = Drone("udpin://0.0.0.0:14540") 
    await drone_object.connect()
    await drone_object.takeoff(15)

    await asyncio.sleep(15) #waits for 15 seconds

    await drone_object.drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    await drone_object.drone.offboard.start()

    await drone_object.move("f", 10, 50) #move forward at 10m/s for 50 meters
    await drone_object.move("r", 10, 50) #move right at 10m/s for 50 meters
    await drone_object.move("b", 10, 50) #move backward at 10m/s for 50 meters
    await drone_object.move("l", 10, 50) #move left at 10m/s for 50 meters

    drone_object.land()


asyncio.run(main()) #executes the full function
