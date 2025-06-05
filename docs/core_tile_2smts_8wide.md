# core_tile_2smts_8wide Module

`core_tile_2smts_8wide.sv` is a top level wrapper that groups two SMT threads with the shared functional units, caches and TLBs. In the final design it will serve as the building block for multi-core systems.

The present stub only exposes clock and reset inputs and does not yet instantiate its submodules.

A minimal Python model (`CoreTile2SMT8Wide`) is provided for unit tests. It only
tracks the number of executed cycles.
