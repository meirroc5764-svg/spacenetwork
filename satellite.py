from space_network_lib import SpaceEntity, DataCorruptedError
from space_network_lib import Packet, SpaceNetwork, TemporalInterferenceError
import time


class Satellite(SpaceEntity):
    def __init__(self, name, distance_from_earth):
        super().__init__(name, distance_from_earth)

    def receive_signal(self, packet):
        print(f"[{self.name}] Received: {packet}")

def attempt_transmission(packet: Packet):
    try:
        space_network.send(packet)
    except TemporalInterferenceError:
        print("waiting,Interference...")
        time.sleep(2)
        attempt_transmission(packet)
    except DataCorruptedError:
        print("Data retrying,corrupted...")
        time.sleep(2)
        attempt_transmission(packet)


space_network = SpaceNetwork(level=2)
space = Satellite("Sat1", 100)
space2 = Satellite("sat2", 200)
packet = Packet("dalbaeb", space, space2)
attempt_transmission(packet)
