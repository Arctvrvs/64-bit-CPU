# Implementation Milestones

This file lists the sequential milestones for developing the RISC-V CPU
according to the project plan.

1. **Foundation Setup**
   - Populate `rtl/` and `tb/` directories.
   - Build the golden reference model and simple regression make targets.

2. **Instruction Fetch and Decode**
   - Write fetch pipeline modules and I-cache.
   - Implement the 8-wide instruction decoder.

3. **Register Files and Rename Stage**
   - Design the architectural and physical register files.
   - Implement rename logic with free list and checkpoints.

4. **Reorder Buffer and Issue Queue**
   - Finish the ROB with 256 entries.
   - Develop reservation stations and 8-wide issue logic.

5. **Execution Units**
   - Integer ALU, Multiply/Divide, Branch, LSU and Vector FMA.
   - Integrate into a common execution stage.

6. **Branch Prediction**
   - Implement BTB, TAGE, RSB and Indirect Predictor.
   - Create a unified predictor top module.

7. **Cache Hierarchy**
   - L1 data and instruction caches.
   - L2 per core and shared L3 with directory coherence.

8. **Memory Management Unit**
   - L1/L2 TLBs and page walker hardware.
   - Connect to LSU and instruction fetch.

9. **SMT and Multi-Core**
   - Arbitration for two hardware threads.
   - Multi-core mesh with routers and L3 slices.

10. **Security and Virtualization Stubs**
    - SMEP/SMAP checks, SGX enclave hooks, SEV encryption.

11. **UVM Verification Infrastructure**
    - Shared UVM components and scoreboards.
    - Regression scripts and coverage reports.

12. **Documentation and Release**
    - Finalize interface documentation and diagrams.
    - Ensure all verification goals are met.
