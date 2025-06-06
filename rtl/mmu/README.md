MMU-related modules including instruction and data TLBs and page walker logic. The RTL models here are simplified behavioral placeholders.

Available modules:
- `tlb_l1_64e_8w` – small 64-entry TLB
- `tlb_l2_512e_8w` – larger second-level TLB
- `page_walker` – single-request page table walker
- `page_walker8` – up to 8 in-flight walk requests
- Python models `tlb_l1.py` and `tlb_l2.py` now track lookup latency and can
  report coverage statistics when a ``CoverageModel`` is supplied. The page
  walker helpers do the same, recording each walk and whether it faulted.
