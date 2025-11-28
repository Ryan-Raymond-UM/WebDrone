# C2 Server
Because the drone and controller might be connected using a variety of network topologies, we want to have a stationary intermediary who can connect the two.
## ws://C2Server:WSPort/drone
Allows one drone at a time to connect.
The other end connects to the controller.
## ws://C2Server:WSPort/controller
Allows one single controller at a time to connect.
The other end connects to the drone.

