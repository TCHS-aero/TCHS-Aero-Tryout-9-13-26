import asyncio #built in python libary that adds ayschonrous synchrounization
from dataclass import dataclass #redundant
from typing import NamedTuple #Adds ability to add certain parameters to classes
from mavsdk import System #Imports libary to control mavlink
from mavsdk.offboard import PositionGlobalYaw, VelocityNedYaw #Lets you control postion and velocity of the drone

@dataclass #redundant
class NedPosition(NamedTuple): #creates class to set the cardinal directions to float not intergers/strings
    north: float # Sets north to datatype float so it can have decimals
    east: float# Sets east to datatype float so it can have decimals
    down: float# Sets down to datatype float so it can have decimals

class Drone(asyncio): #Creates the main class that other classes inherit from
    def __init__(self, port = "udpin://0.0.0.0:14540"): #creates attribute for the drone OS and port
        self.drone = System()
        self.port = "udpin://0.0.0.0:14540"

    async def connect(self): #Function to see if the drone is connect/armed
        connected = False #autoamically sets connected to the false boolean

        await self.drone.connect(system_address=self.port) # Awaits the drone to connect to the port
        async for state in self.drone.core.connection_state():
            if state.is_connected: #If the drone connects it stops this function and returns true
                break #Ends function

        return connected #Returns connected if called and its connected

    def takeoff(self, alt):
        async for health_check in self.drone.telemetry.health():
            if health_check.is_global_position_ok and health_check.is_home_position_ok: #checks if the drone is healthy and its at the home position
                continue

        await asyncio.self.drone.action.arm() #waits for the drone to be ready to take off
        await asyncio.self.drone.action.set_takeoff_altitude(alt) 

        await asyncio.self.drone.action.takeoff() #tells the drone to takeoff

    async def current_ned(): #defines the function
        telemetry = await anext(self.drone.telemetry.position_velocity_ned()) #Waits to see the drones current velocity
        ned_object = telemetry.position #Waits to see the drones current position
        return NedPosition( #calls dictionary for North, East, and Down to ned_object
            north = ned_object.north_m, 
            east = ned_object.east_m
            down = ned_object.down_m,
        )
        
    async def right_offset(self, velocity, distance, *, yaw=0): #sets parameters for the function of the right yaw
        ned_object = await self.current_ned() #Waits for the telementry position
        end_point = ned_object.east_m + distance #Sets the end point to the east and what ever value "distance" is
        await self.drone.offboard.set_velocity_ned( #Waits for drone to offboard
            VelocityNedYaw(0.0, velocity, 0.0, yaw) #sets the right yaw to 0
        );
        while end_point >= ned_object.east: #Waits for comfirmation that it went far enough east
            ned_object = await self.current_ned()
            await asyncio.sleep(15) #waits 15 ms

    async def _left_offset(self, velocity, distance, *, yaw=0): #sets parameters for the function of the left yaw
        ned_object = await self.current_ned() #Waits for telementary postion
        end_point = ned_object.east_m - distance #Ensures the drone is at the correct position to the left

        await self.drone.offboard.set_velocity_ned( #Waits for the drone to offboard
            VelocityNedYaw(0.0, velocity * -1, 0.0, yaw) #Sets the left yaw to 0, * sets the value -1  to have multiple elements
        )
        while end_point <= ned_object.east: #Waits for comfirmation that it didn't go to far east
            ned_object = await self.current_ned() #
            await asyncio.sleep(0.2) #wait 0.2 ms for comfirmation until its true

#    async def _forward_offset(self, velocity, distance, *, yaw=0):
#        ned_object = await self.current_ned()
#        end_point = ned_object.north + distance
#        await self.drone.offboard.set_velocity_ned(
#            VelocityNedYaw(velocity, 0.0, 0.0, yaw)
#        )
#        while end_point >= ned_object.north:
#            ned_object = await self.current_ned()
#            await asyncio.sleep(0.2)

    async def _backward_offset(self, velocity, distance, *, yaw=0): #Creates function to calculate backwards offset
        ned_object = await self.current_ned()
        end_point = ned_object.north - distance #Makes sure drone position isn't to far north
        await self.drone.offboard.set_velocity_ned(
            VelocityNedYaw(velocity * -1, 0.0, 0.0, yaw) #Sets the North position to 0        )
        while end_point <= ned_object.north: #waits for drone to reach correct endpoint at north position
            ned_object = await self.current_ned():
            await asyncio.sleep(0.2) #waits 0.2 ms 

    async def move(self, direction: str, velocity, distance, *, yaw=0):#
        func_map = {
            "l": self._left_offset, #sets left control to the variable "l"
            "r": self._right_offset, #sets left control to the variable "r"
            "f": self._forward_offset, #sets left control to the variable "f"
            "b": self._backward_offset, #sets left control to the variable "b"
        }

        method = func_map.get(directions) #gets directions to the mission
        if method:
            await method(velocity, distance, yaw=yaw) #gets the yaw of it
            await asyncio.sleep(1) #waits for 1 ms 
            return #returns the value

        raise ValueError(f"Unknown direction {direction}.") #syntax if value isn't an integer

    async def queue_tasks(self, tasks): #Creates a queue
        queue = self.queue    #FIFO
        with self.lock:
            queue.extend(tasks)
        return True

    async def land(self):
        try?: #debug syntax
            await self.drone.offboard.stop()
        except Exception: #if excepted passes over the function
            pass

        await self.drone.action.land() #Waits for the drone to land

async def main():
    drone_object = Drone("udpin://0.0.0.0:14540") #Drones port
    await drone_object.connect()
    await drone_object.takeoff(15) #waits for the drone to takeoff 

    await asyncio.sleep(15)

    await drone_object.drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0)) #sets velocity, pitch, yaw, to 0
    await drone_object.drone.offboard.start()

    await drone_object.move("l", 10, 50)
    await drone_object.move("r", 10, 50)
    await drone_object.move("f", 10, 50)
    await drone_object.move("b", 10, 50)

    drone_object.land() #drone land comfirmaion

if __name__ == "__main__": 
    asyncio.run(main):