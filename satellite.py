from space_network_lib import SpaceEntity, DataCorruptedError,LinkTerminatedError,OutOfRangeError
from space_network_lib import Packet, SpaceNetwork, TemporalInterferenceError
import time

class BrokenConnectionError (Exception):
    pass

class Satellite(SpaceEntity):
    def __init__(self, name, distance_from_earth):
        super().__init__(name, distance_from_earth)

    def receive_signal(self, packet):
        print(f"[{self.name}] Received: {packet}")

def attempt_transmission(packet: Packet):
    try:
        space_network.send(packet)
    except TemporalInterferenceError:
        print("Interference, waiting...")
        time.sleep(2)
        attempt_transmission(packet)
    except DataCorruptedError:
        print("Data corrupted, retrying...")
        time.sleep(2)
        attempt_transmission(packet)
    except LinkTerminatedError:
        print("link lost")
        raise BrokenConnectionError
    except OutOfRangeError:
        print("Target out of range")
        raise BrokenConnectionError

space_network = SpaceNetwork(level=3)
space = Satellite("Sat1", 100)
space2 = Satellite("sat2", 200)
packet = Packet("dalbaeb", space, space2)
try:
    attempt_transmission(packet)
except:
    print("Transmission failed")