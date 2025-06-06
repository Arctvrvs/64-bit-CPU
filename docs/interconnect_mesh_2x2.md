# interconnect_mesh_2x2 Module

`interconnect_mesh_2x2.sv` instantiates four `router_5port` blocks arranged in a small 2×2 mesh. It is used to connect L2 caches and L3 cache slices in the top-level SoC.

## Description

Each router links to its north, south, east and west neighbors with a simple credit based hand-shake. The current behavioral model just wires each router's outputs directly to the neighbor inputs without buffering.

For unit tests a small Python helper `InterconnectMesh2x2` mirrors this behavior.
