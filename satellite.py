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
        #space_network.send(packet)
        if isinstance(packet, RelayPacket):
            inner_packet = packet.data
            print(f"Unwrapping and forwarding to {inner_packet.receiver}{packet.sender}")
            attempt_transmission(packet.data)
        else:
            print(f"Final destination reached: [{packet.data}] from {packet.sender.name}")
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
class RelayPacket(Packet):
    def __init__(self, packet_to_relay, sender,proxy):
        super().__init__(packet_to_relay, sender,proxy)
    def __repr__(self):
        return RelayPacket(f"[{self.data}] "
                           f"to {self.receiver} from {self.sender}")

space_network = SpaceNetwork(level=4)
space=Satellite("Earth",0)
space1 = Satellite("Sat1", 100)
space2 = Satellite("sat2", 200)
#packet = Packet("dalbaeb", space, space2)
p_final=Packet("hello from the Earth",space1,space2)
p_earth_to_sat1=RelayPacket(p_final,space,space1)
try:
    attempt_transmission(p_earth_to_sat1)
except BrokenConnectionError:
    print("Transmission failed")