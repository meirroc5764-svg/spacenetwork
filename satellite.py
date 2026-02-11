from space_network_lib import SpaceEntity, DataCorruptedError, LinkTerminatedError, OutOfRangeError
from space_network_lib import Packet, SpaceNetwork, TemporalInterferenceError
import time


class BrokenConnectionError(Exception):
    pass


class Satellite(SpaceEntity):
    def __init__(self, name, distance_from_earth):
        super().__init__(name, distance_from_earth)

    def receive_signal(self, packet):
        print(f"[{self.name}] Received: {packet}")


def attempt_transmission(packet: Packet):
    try:
        space_network.send(packet)
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
    def __init__(self, packet_to_relay, sender, proxy):
        super().__init__(packet_to_relay, sender, proxy)

    def __repr__(self):
        return (f"RelayPacket(Relaying [{self.data}] "
                f"from {self.sender} to {self.receiver}) ")


space_network = SpaceNetwork(level=5)
space = Satellite("Earth", 0)
space1 = Satellite("Sat1", 100)
space2 = Satellite("sat2", 200)
space3 = Satellite("sat3", 300)
space4 = Satellite("sat4", 400)
start_packet = Packet("dalbaeb", space, space2)
p_final = Packet("hello from the Earth", space3, space4)
p_earth_to_sat3 = RelayPacket(p_final, space2, space3)
p_earth_to_sat2 = RelayPacket(p_earth_to_sat3, space1, space2)
p_earth_to_sat1 = RelayPacket(p_earth_to_sat2, space, space1)
all_sates = [space, space1, space2, space3, space4]
num = 0


def packet_send_smart(all_sate, packet: Packet):
    global num
    distance = abs(start_packet.receiver.distance_from_earth -
                   packet.sender.distance_from_earth
                   )
    if distance > 100:
        packet1 = RelayPacket(packet, all_sate[num], all_sate[num + 1])
        try:
            attempt_transmission(packet1)
        except BrokenConnectionError:
            print("Transmission failed")
        num += 1
        distance -= 100
        packet_send_smart(all_sate, packet1)

    else:
        packet = Packet(packet.data, packet.sender, packet.receiver)
        try:
            attempt_transmission(packet)
        except BrokenConnectionError:
            print("Transmission failed")
            return


packet_send_smart(all_sates, start_packet)

