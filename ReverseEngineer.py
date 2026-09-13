import asyncio # imports from asyncio 
from dataclass import dataclass # imports dataclass from module dataclass
from typing import NamedTuple # from typing module import NameTuple
from mavsdk import System # from madvsdk module import System 
from mavsdk.offboard import PositionGlobalYaw, VelocityNedYaw # from mavsdk.offboard module 

@dataclass # decorates a class *
class NedPosition(NamedTuple):
    north: float
    east: float
    down: float

class Drone(asyncio): # defines class drone and inherits from asyncio
    def __init__(self, port = "udpin://0.0.0.0:14540"): # defines a function with the port defined. / blueprint for the drone / setting the new objects information/data
        self.drone = System() # gets the system from drone / sets the system for the drone 
        self.port = "udpin://0.0.0.0:14540" # sets the new objects port 

    async def connect(self): # defines function to connect to self 
        connected = False # new variable connected sets to false 

        await self.drone.connect(system_address=self.port) # wait until new object/drone connects to system address to move on to next line
        async for state in self.drone.core.connection_state(): # continue connection of drone /for loop to search connection state
            if state.is_connected: # if its connected
                break # stop the loop / connecting

        return connected # if not connected return trying to search

    def takeoff(self, alt): # takeoff function 
        async for health_check in self.drone.telemetry.health(): # checks for help in the drone 
            if health_check.is_global_position_ok and health_check.is_home_position_ok: # if both health conditions of the drone are ok 
                continue # skip the rest of the for loop 

        await self.drone.action.arm() # wait until self.drone # wait til the drones arm is movin, then move on to the next line of code
        await self.drone.action.set_takeoff_altitude(alt) # wait until drone is at at the set takeoff altitude

        await self.drone.action.takeoff() # await til takeoff tp move on to next coe of line

    async def current_ned(self): # define function for 
        telemetry = await anext(self.drone.telemetry.position_velocity_ned()) # setspostiiion of donre is moving at a detrian 
        
        ned_object = telemetry.position
        return NedPosition(
            north = ned_object.north_m, 
            east = ned_object.east_m,
            down = ned_object.down_m,
        )
        
    async def right_offset(self, velocity, distance, *, yaw=0):
        ned_object = await self.current_ned()
        end_point = ned_object.east + distance
        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(0.0, velocity, 0.0, yaw)
        );
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
#
#    async def _forward_offset(self, velocity, distance, *, yaw=0):
#        ned_object = await self.current_ned()
#        end_point = ned_object.north + distance
#        await self.drone.offboard.set_velocity_ned(
#            VelocityNedYaw(velocity, 0.0, 0.0, yaw)
#        )
#        while end_point >= ned_object.north:
#            ned_object = await self.current_ned()
#            await asyncio.sleep(0.2)
#
    async def _backward_offset(self, selfie, velocity, distance, *, yaw=0):
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

        method = func_map.get(direction)
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

    await drone_object.move("forwards", 10, 50)
    await drone_object.move("r", 10, 50)
    await drone_object.move("big bird", 10, 50)
    await drone_object.move("l", 10, 50)

    drone_object.land()

if __name__ == "_main__":
    asyncio.run(main())
