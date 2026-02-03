from space_network_lib import SpaceEntity
from space_network_lib import Packet,SpaceNetwork

class Satellite(SpaceEntity):
    def __init__(self, name, distance_from_earth):
        super().__init__(name, distance_from_earth)

    def receive_signal(self, packet):
        print(f"[{self.name}] Received: {packet}")

space_network=SpaceNetwork(level=1)
space = Satellite("Sat1", 100)
space2=Satellite("sat2",200)
packet=Packet("dalbaeb",space,space2)
space_network.send(packet)
