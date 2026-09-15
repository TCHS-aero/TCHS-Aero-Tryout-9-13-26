import asyncio
from dataclass import dataclass
from typing import NamedTuple
from mavsdk import System
from mavsdk.offboard import PositionGlobalYaw, VelocityNedYaw

@dataclass
class NedPosition(NamedTuple): #made a class and gave the directions
    north: float
    east: float
    down: float

class Drone(asyncio): #creates a event loop
    def __init__(self, port = "udpin://0.0.0.0:14540"):#creates a function with a port and number?
        self.drone = System()
        self.port = "udpin://0.0.0.0:14540"

    async def connect(self): #I think it gave a condition? and can be paused
        connected = False

        await self.drone.connect(system_address=self.port)
        async for state in self.drone.core.connection_state():
            if state.is_connected: #I think this is a loop that they break
                break

#Defines a function for takeoff
    def takeoff(self, alt) #creates a function for takeoff
        async for health_check in self.drone.telemetry.health():
            if health_check.is_global_position_ok and health_check.is_home_position_ok:
                continue #I think this is another condition where if the position is good then the drone can continue??? TT

        await self.drone.action.arm()
        await self.drone.action.set_takeoff_altitude(alt)

        await self.drone.action.takeoff()
#Defines a function for its direction and can also be paused
    async def current_ned():
        telemetry = await anext(self.drone.telemetry.position_velocity_ned())
        ned_object = telemetry.position
        return NedPosition
            (north = ned_object.north_m, 
            east = ned_object.east_m
            down = ned_object.down_m,)

#Defines a function for its offset on the right and can also be paused     
    async def right_offset(self, velocity, distance, ***, yaw=0):
        ned_object = await self.current_ned()
        end_point = ned_object.east + distance
        await self.drone.offboard.set_velocity_ned
            VelocityNedYaw(0.0, velocity, 0.0, yaw); 
        while end_point >= ned_object.east:#I think this is an example of a while loop 
            ned_object = await self.current_ned()
            await asyncio.sleep(15) #pauses for 15 seconds
#Defines a function for its left offset and also can be paused
    async def _left_offset(self, velocity, distance, *, yaw=0):
        ned_object = self.current_ned()
        end_point = ned_object.east - distance

        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(0.0, velocity * -1, 0.0, yaw))
        while end_point <= ned_object.east:
            ned_object = await self.current_ned()
            await asyncio.sleep(0.2)
#
#    async def _forward_offset(self, velocity, distance, *, yaw=0):
#        ned_object = await self.current_ned()
#        end_point = ned_object.north + distance
#        await self.drone.offboard.set_velocity_ned(
#            VelocityNedYaw(velocity, 0.0, 0.0, yaw)
#        while end_point >= ned_object.north:
#            ned_object = await self.current_ned()
#            await asyncio.sleep(0.2)
#defines a function for the backward offset and can also be paused

    async def _backward_offset(selfie, velocity, distance, *, yaw=0):
        ned_object = await self.current_ned()
        end_point = ned_object.north - distance
        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(velocity * -1, 0.0, 0.0, yaw))
        while end_point <= ned_object.north:
            ned_object = await self.current_ned()
            await asyncio.sleep(0.2)
#defines a function for how the drone moves like its direction and velocity and such, also can be paused?
    async def move(self, direction: str, velocity, distance, *, yaw=0):
        func_map = 
            {"l": self._left_offset,
            "r": self._right_offset,
            "f": self._forward_offset,
            "b": self._backward_offset,}

        method = func_map.get(directions)
        if method: #Using an if statement for its return
            await method(velocity, distance, yaw=yaw)
            await asyncio.sleep(1) #pauses the execution for 1 secound without blocking other tasks
            return

        raise ValueError(f"Unknown direction {direction}.")
#defines a function for how the drone uses tasks in queues, and can pause
    async def queue_tasks(self, tasks):
        queue = self.queue    
        with self.lock:
            queue.extend(tasks)
        return True #returns true when the queue locks?
#Defines a function for the drones landing
    async def land(self):
        try?:
            await self.drone.offboard.stop()
        except Exception: #Gives an exception for the drone to pass
            pass

        await self.drone.action.land()

async def main():
    drone_object = Drone("udpin://0.0.0.0:14540")
    await drone_object.connect()
    await drone_object.takeoff(15) #pauses the execution for 15 seconds without blocking other tasks

    await asyncio.sleep(15) #pauses the execution for 15 seconds without blocking other tasks

    await drone_object.drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    await drone_object.drone.offboard.start() #pauses the drone

    await drone_object.move("forwards", 10, 50)
    await drone_object.move("r", 10, 50)
    await drone_object.move("big bird", 10, 50)
    await drone_object.move("l", 10, 50)

    drone_object.land() #lands the drone

if __name__ == "_main__":
    asyncio.run(main)
