import asyncio #import asyncio function which defines async for the rest of the code
from dataclass import dataclass #import a thing that can contains variables in the class
from typing import NamedTuple #
from system import mavsdk #gets soemthing from the system and imports mavsdk which is a collection of libararies for carious programming langues to interface with MAVLink, such as drone
from mavsdk.offboard import PositionGlobalYaw, VelocityNedYaw

@dataclass #calling dataclass to be used
class NedPosition(NamedTuple): #makes a class/blueprint of a thing called NedPosition where we can pull variables from it easily
    float north; #create a floating variable named north
    float east; #create a floating variable named east
    float down; #create a floating variable named down

class Drone(asyncio): #create a class called drone using asyncio
    def __init__(self, drone, port = "udpin://0.0.0.0:14540"): # define the function _init_ with the parameters of self, port, which connects it to the drone (witht he port specififed)
        self.drone = system() #calling drone of the self name to be system()
        self.port = "udpin://0.0.0.0:14540" #defining the address of the port of self 

    async def connect(self): #define connect(slef) function with async; async just returns a coroutine object
        connected = False

        await self.drone.connect(system_address=self.port) #wait for the dron to connect to your computer
        async for state in self.drone.core.connection_state(): #detects the connection state and save it in the value state
            if state.is_connected: #check if the statement is true
                break #exits the loop

        return connected 

    def takeoff(self, alt): #define the function takeoff with the parameter slef, alt
        async for health_check in self.drone.telemetry.health(): #detecting for health_check value in self.drone.telemetry.health()
            if health_check.is_global_position_ok and health_check.is_home_position_ok: #check if the statement is true
                continue #continue the loop

        await self.drone.action.arm() #wait for the drone arm to be activated, it waits for it
        await self.drone.action.set_takeoff_altitude(alt) #wait for the drone to process the take off command

        await self.drone.action.takeoff() #wait fot the drone to take off

    async def current_ned(): #define the function current_ned() 
        telemetry = await anext(self.drone.telemetry.position_velocity_ned())
        ned_object = telemetry.position #store ned_object into telementery.position
        return NedPosition(
            north = ned_object.north_m, #store the float number into north
            east = ned_object.east_m, #store the float number into east
            down = ned_object.down_m,#store the float number into down
        )
        
    async def right_offset(self, velocity, distance, ***, yaw=0): #define right_offset with those variables.
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
        try?:
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
