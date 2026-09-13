import asyncio
from dataclasses import dataclass 
from typing import NamedTuple 
from mavsdk import System
from mavsdk.offboard import PositionGlobalYaw, VelocityNedYaw
#imports necessary libraries to run script, like mavsdk to get access to drone functions, asyncio for asyncronous scripts and dataclasses to import tuples, strings, and whatnot


@dataclass
class NedPosition(NamedTuple):
    north: float
    east: float
    down: float
    #declares NedPosition class that inherits the library NamedTuple so in the class north, east, and down can inherit float from NamedTuple

class Drone(asyncio): #Creates drone object that inherits library asyncio 
    def __init__(self, port): #initalizes class and states self and port, sets port to the provided udpin
        self.drone = System() #creates self.drone from System() class
        self.port = port #sets self.port to the already states port in init()

    async def connect(self): #creates async def function called connect
        connected = False #sets connected variable to false 

        await self.drone.connect(system_address=self.port) #awaits for the script to connect to the drone, setting the system address to self.port
        async for state in self.drone.core.connection_state(): #runs a for loop in which connection_state constantly outputs information, and that info is set to state. 
            if state.is_connected: #checks if state is connected 
                break #if connection successful, breaks out of the loop to continue code. If not, keeps retrying until success

        return connected #returns connecting output

    async def takeoff(self, alt): #creates async def takeoff function with parameters self and alt
        async for health_check in self.drone.telemetry.health(): #runs for loop that self.drone.telemetry.health() constantly gives information, and that information is set to health_check
            if health_check.is_global_position_ok and health_check.is_home_position_ok: #compares if health_check's parameters are true 
                continue #if true, skips this element

        await self.drone.action.arm() #sends a request to the script to arm the drone
        await self.drone.action.set_takeoff_altitude(alt) #sends a request to set the takeoff altitute of the drone to variable 'alt'

        await self.drone.action.takeoff() #sends a request to takeoff the drone, as the drone has been armed and takeoff altitute has been specified

    async def current_ned(self): #creates async def takeoff function with parameter self
        telemetry = await next(self.drone.telemetry.position_velocity_ned()) #sets telemetry to the next iteration of the iterator self.drone.telemetry.position_velocity_ned() and awaits
        ned_object = telemetry.position #sets ned_object to telemetry.position
        return NedPosition(
            north = ned_object.north_m, 
            east = ned_object.east_m,
            down = ned_object.down_m
        ) #returns a NedPosition() object with north, east, down in the object being set to the Ned object's north_m, east_m, and down_m, respectively
    
    async def _right_offset(self, velocity, distance, *, yaw=0): #creates async def _right_offset with parameters self, velocity, distance, a keyword argument, and sets yaw to 0.
        ned_object = await self.current_ned() #sets ned_object to the NedPosition() that was returned in self.current_ned()
        end_point = ned_object.east + distance #grabs ned_object's parameter east and adds the value distance to it, sets it to end point
        await self.drone.offboard.set_velocity_ned( #sets the velocity_ned of the drone to a VelocityNedYaw() object, with its north_n_s, east_n_s, and down_m_s to the respective variables, while yaw is set to 0.
            VelocityNedYaw(0.0, velocity, 0.0, yaw)
        ) #awaits for 
        while end_point >= ned_object.east: #if the distance of origin-end_point is greater than the distance of origin-drone east, keep refreshing the ned object with new telemetry and wait 15 seconds.
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

    async def _forward_offset(self, velocity, distance, *, yaw=0):
        ned_object = await self.current_ned()
        end_point = ned_object.north + distance
        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(velocity, 0.0, 0.0, yaw)
        )
        while end_point >= ned_object.north:
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
            "b": self._backward_offset
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

async def main():
    drone_object = Drone("udpin://0.0.0.0:14540")
    await drone_object.connect()
    await drone_object.takeoff(15)

    await asyncio.sleep(15)

    await drone_object.drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    await drone_object.drone.offboard.start()

    await drone_object.move("f", 10, 50)
    await drone_object.move("r", 10, 50)
    await drone_object.move("b", 10, 50)
    await drone_object.move("l", 10, 50)

    await drone_object.land()

if __name__ == "__main__":
    asyncio.run(main())
