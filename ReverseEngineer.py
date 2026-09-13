import asyncio # import asyncio
from dataclass import dataclass # we import dataclass from dataclass
from typing import NamedTuple # from the library typing, we import NamedTuple
from mavsdk import System # we import system from mavsdk
from mavsdk.offboard import PositionGlobalYaw, VelocityNedYaw # we import the yaws from mavsdk

@dataclass

class NedPosition(NamedTuple): # this class is defining the directions, a child class of NamedTuple
                               # ***NED STANDS FOR NORTH, EAST, DOWN***
    def __init__(self): # initializing the class, only parameter is self
        self.north: float # we define north as a float
        self.east: float # we define east as a float
        self.down: float # we define down as a float

class Drone(asyncio): # this class is creating the drone, a child class of asyncio and connecting it to our system address
    def __init__(self, port = "udpin://0.0.0.0:14540"): # initializing
        self.drone = System() # we create the drone
        self.port = port # we redefine port

    async def connect(self): # new method called connect with parameter self
        connected : bool = False # the variable connected is defined as a boolean and is false

        await self.drone.connect(system_address=self.port) # wait for the drone to connect to me
        async for state in self.drone.core.connection_state(): 
            if state.is_connected: # when the drone is connected, set connected to true now
                connected = True
                break # break the loop

        return connected # If we are not connected, then it is false and the loop remains.
                         # If we ARE connected, then it is true and the loop breaks.

    def takeoff(self, alt): # we takeoff
        async for health_check in self.drone.telemetry.health():
            if health_check.is_global_position_ok and health_check.is_home_position_ok:
                continue
            else:
                return
                # we check if global position and home position is ok. If not we return

        await self.drone.action.arm() 
        await self.drone.action.set_takeoff_altitude(alt)

        await self.drone.action.takeoff() # we arm, we set altitude, then takeoff

    async def current_ned(self): # define current north, east, down
        telemetry = await anext(self.drone.telemetry.position_velocity_ned()) # await drone position and velocity
        ned_object = telemetry.position
        return NedPosition(
            north = ned_object.north_m, # we return the north, east, and down of the drone
            east = ned_object.east_m    # as a ned object
            down = ned_object.down_m,
        )
        
    async def _right_offset(self, velocity, distance, *, yaw=0): # define right offset
        ned_object = await self.current_ned() # wait for method above
        end_point = ned_object.east + distance # define endpoint as east + distance
        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(0.0, velocity, 0.0, yaw)) 
        while end_point >= ned_object.east: # when endpoint >= east of ned_object
            ned_object = await self.current_ned()
            await asyncio.sleep(0.2) # we've reached our endpoint

    async def _left_offset(self, velocity, distance, *, yaw=0): # define left offset
        ned_object = await self.current_ned() # wait for current ned
        end_point = ned_object.east - distance # endpoint as east - distance

        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(0.0, velocity * -1, 0.0, yaw))
        while end_point <= ned_object.east: # when endpoint <= east of ned_object
            ned_object = await self.current_ned()
            await asyncio.sleep(0.2) # we've reached our endpoint

    async def _forward_offset(self, velocity, distance, *, yaw=0): # define forward offset
        ned_object = await self.current_ned() # wait for current ned
        end_point = ned_object.north + distance # define endpoint as north + distance
        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(velocity, 0.0, 0.0, yaw)) 

        while end_point >= ned_object.north: # when endpoint >= north of ned_object
            ned_object = await self.current_ned()
            await asyncio.sleep(0.2) # we've reached our endpoint

    async def _backward_offset(self, velocity, distance, *, yaw=0): #define backward offset
        ned_object = await self.current_ned() 
        end_point = ned_object.north - distance # define endpoint as north - distance
        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(velocity * -1, 0.0, 0.0, yaw))

        while end_point <= ned_object.north: # endpoint <= north of ned_object
            ned_object = await self.current_ned()
            await asyncio.sleep(0.2) # we've reached our endpoint

    async def move(self, direction: str, velocity, distance, *, yaw=0):
        func_map = {
            "l": self._left_offset, # we use the offsets we defined and make a dictionary out of them
            "r": self._right_offset,  # l = left, r = right, f = forward, b = back
            "f": self._forward_offset,
            "b": self._backward_offset,
        }

        method = func_map.get(directions)
        if method:
            await method(velocity, distance, yaw=yaw)
            await asyncio.sleep(1) # we get the directions from function map
            return

        raise ValueError(f"Unknown direction {direction}.") # if there's a cool error it stops and says unknown direction

    async def queue_tasks(self, tasks):
        queue = self.queue    
        with self.lock:
            queue.extend(tasks) # we extend the queue by tasks
        return True

    async def land(self):
        try:
            await self.drone.offboard.stop() # await the drone to offboard
        except Exception: # except for an exception
            pass

        await self.drone.action.land() # then we land

async def main(): # define main
    drone_object : Drone = Drone("udpin://0.0.0.0:14540") # it is connected to my system address
    await drone_object.connect() # connect to drone
    await drone_object.takeoff(15) # takeoff 15

    await asyncio.sleep(15)

    await drone_object.drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    await drone_object.drone.offboard.start() # we set velocity based on the velocity and ned we tracked
                                              # then we start
    await drone_object.move("f", 10, 50) # forward 10 velocity 50 distance
    await drone_object.move("r", 10, 50)# right 10 velocity 50 distance
    await drone_object.move("b", 10, 50)# back 10 velocity 50 distance
    await drone_object.move("l", 10, 50)# left 10 velocity 50 distance

    await drone_object.land() # we land

if __name__ == "__main__": # IF WE ARE RUNNING MAIN FILE RUN MAIN FUNCTION
    asyncio.run(main())
