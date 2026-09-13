import asyncio 
from time import sleep
from dataclass import dataclass 
from typing import NamedTuple 
from system import mavsdk 
from mavsdk.offboard import PositionGlobalYaw, VelocityNedYaw

class Drone(asyncio):
    def __init__(self, drone, port = "udpin://0.0.0.0:14540"): 
        self.drone = system() 
        self.port = "udpin://0.0.0.0:14540" 
    async def connect(self): 
        connected = False

        await self.drone.connect(system_address=self.port) 
        async for state in self.drone.core.connection_state(): 
            if state.is_connected: 
                break 

        return connected 

    def takeoff(self, alt): 
        async for health_check in self.drone.telemetry.health(): 
            if health_check.is_global_position_ok and health_check.is_home_position_ok: 
                continue
    async def move(self, direction: str, velocity, distance, yaw=0):
        func_map = {
            "l": self._left_offset,
            "r": self._right_offset,
            "f": self._forward_offset,
            "b": self._backward_offset,
        }
    async def land(self):
        try?:
            await self.drone.offboard.stop()
        except Exception:
            pass

        await self.drone.action.land()

async def main():
    drone_object = Drone("udpin://0.0.0.0:14540")
    await drone_object.connect()
    await drone_object.takeoff(5)

    await asyncio.sleep(10)

    await drone_object.move("forwards", 5, 10)

    drone_object.land()

asyncio.run(main())

#Arthur Niu, aniu5117@tcusd.net
#Duke Fong, dfong5066@tcusd.net