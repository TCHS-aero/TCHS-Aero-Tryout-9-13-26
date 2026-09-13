import asyncio # Imports asyncio so that you can access the library asyncio
from dataclasses import dataclass # Imports the library dataclass
from typing import NamedTuple  # Imports NamedTuple form the library typing
from mavsdk import System # Imports System from the library mavsdk, so that you can access the library named System.
from mavsdk.offboard import PositionGlobalYaw, VelocityNedYaw # Imports from the library mavsdk.offboard, PositionGlobalYaw and VelocityNedYaw.

@dataclass
class NedPosition(NamedTuple): # Creates a class named NedPosition that uses the parameter library NamedTuple
    north: float # Sets north value as a float
    east: float # Sets east value as a float
    down: float # Sets down value as a float

class Drone(asyncio): # Creates a class named Drome that takes the parameter library asyncio
    def __init__(self, port = "udpin://0.0.0.0:14540"): # This initializes the serial number for the drone to connect
        self.drone = System() # This creates a system object named drome
        self.port = "udpin://0.0.0.0:14540" # This creates a object named port that connects to the drone

    async def connect(self): # makes a function named connect that will conenct to the syetem object named drone from the port serial number.
        connected = False # sets the connection to the drone as false

        await self.drone.connect(system_address=self.port) # This will create a connection to the drone using the system object named port
        async for state in self.drone.core.connection_state(): # This gets the connection state of the drone.
            if state.is_connected: # An if statement that sees if the drone is connected.
                return connected  # returns connected and states that you are connected to the drone

    def takeoff(self, alt) # makes a function named takeoff that accepts 2 parameters, self and alt
        for health_check in self.drone.telemetry.health(): # Looks for health_check in the self function drone.telemetry.health
            if health_check.is_global_position_ok and health_check.is_home_position_ok: # sees if the drone has a global position and if the drone is in it's home position
                continue # if both standards are met, it will continue

        self.drone.action.arm() # Arms takeoff
        self.drone.action.set_takeoff_altitude(alt) # Sets what altitude the drone will go when it takes off

        self.drone.action.takeoff() # takes off

    async def current_ned(): # Creates a fucntion named current_ned
        telemetry = await anext(self.drone.telemetry.position_velocity_ned()) # sets the next postion and velocity status to variable telemetry
        ned_object = telemetry.position # sets the position status to the variable ned_object
        return NedPosition(
            north = ned_object.north_m, # sets the north value to variable north
            east = ned_object.east_m, # sets the east value to variable east
            down = ned_object.down_m, # sets the down value to variable down
        )
        
    async def right_offset(self, velocity, distance, ***, yaw=0): # makes a function named right_offset and having the parameters self, velocity, distance, variadic arguments, and sets yaw to 0 
        ned_object = await self.current_ned()
        end_point = ned_object.east + distance # sets the endpoint variable to the object's east value plus the distance value
        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(0.0, velocity, 0.0, yaw)
        )
        while end_point >= ned_object.east: # While the end_point is greater than or equal to the drone's east value
            ned_object = await self.current_ned() 
            await asyncio.sleep(15) # sleep for 15 sec

    async def _left_offset(self, velocity, distance, *, yaw=0):
        ned_object = self.current_ned()
        end_point = ned_object.east - distance # end_point equals the object value east minus the distance

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

async def main():
    drone_object = Drone("udpin://0.0.0.0:14540")
    await drone_object.connect() #connects
    await drone_object.takeoff(15)  #takes off

    await asyncio.sleep(15) # pauses the code for 15 seconds

    await drone_object.drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    await drone_object.drone.offboard.start()

    await drone_object.move("forwards", 10, 50)
    await drone_object.move("r", 10, 50)
    await drone_object.move("big bird", 10, 50)
    await drone_object.move("l", 10, 50)

    drone_object.land() # Lands the drone

if __name__ == "_main__":
    asyncio.run.main() # runs the script
