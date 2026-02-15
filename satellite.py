from space_network_lib import SpaceEntity, DataCorruptedError, LinkTerminatedError, OutOfRangeError
from space_network_lib import Packet, SpaceNetwork, TemporalInterferenceError
import time


class BrokenConnectionError(Exception):
    pass


class Satellite(SpaceEntity):
    def __init__(self, name, distance_from_earth,key):
        super().__init__(name, distance_from_earth)
        self.key=key

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
class EncryptedPacket(Packet):
    def __init__(self,data,sender,receiver,key):
        self.key=key
        encrypted_data = self._encrypt(data)
        super().__init__(encrypted_data, sender, receiver)
    def _encrypt(self,data):

            if isinstance(data, bytes):
                data_bytes = data  # уже байты
            else:
                data_bytes = data.encode('utf-8')  # строка → байты

            encrypted_bytes = bytes([b ^ self.key for b in data_bytes])
            return encrypted_bytes


space_network = SpaceNetwork(level=7)
space = Satellite("Earth", 0,45)
space1 = Satellite("Sat1", 100,46)
space2 = Satellite("sat2", 200,55)
space3 = Satellite("sat3", 300,66)
space4 = Satellite("sat4", 400,33)
start_packet = Packet("dalbaeb", space, space2)
p_final = EncryptedPacket("hello from the Earth", space3, space4,47)
p_earth_to_sat3 = RelayPacket(p_final, space2, space3)
p_earth_to_sat2 = RelayPacket(p_earth_to_sat3, space1, space2)
p_earth_to_sat1 = RelayPacket(p_earth_to_sat2, space, space1)
all_sates = [space, space1, space2, space3, space4]
num = 0


def packet_send_smart(all_sate, packet: Packet):
    global num
    if num >= len(all_sate) - 1:
        print("Relay chain ended")
        return
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
        distance-=100
        new_packet = Packet(
            packet.data,
            all_sate[num],
            packet.receiver
        )
        packet_send_smart(all_sate, new_packet)

    else:
        packet = Packet(packet.data, packet.sender, packet.receiver)
        try:
            encryptedPacket=EncryptedPacket(packet.data, packet.sender,
                            packet.receiver, packet.receiver.key)
            attempt_transmission(encryptedPacket)
        except BrokenConnectionError:
            print("Transmission failed")
            return

encryptedPacket=EncryptedPacket(start_packet.data,start_packet.sender,start_packet.receiver,start_packet.receiver.key)
packet_send_smart(all_sates,encryptedPacket )

