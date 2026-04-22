"""
============================================================
  Operating System Lab (ENCA252)
  Lab Assignment 3 — Page Replacement Algorithms
------------------------------------------------------------
  Student  : Anurag Kumar Mishra
  Roll No  : 2401201076
  Course   : BCA (Artificial Intelligence & Data Science)
  Uni      : K.R. Mangalam University, School of Engg & Tech
  Faculty  : Dr. Jyoti Yadav
============================================================
"""

import sys
from collections import deque


# ──────────────────────────────────────────────────────────
#  Utility
# ──────────────────────────────────────────────────────────

def display_step(step_no, page_no, frame_snapshot, is_fault):
    tag = "MISS" if is_fault else "HIT"
    snapshot = list(frame_snapshot)
    print(f"  Step {step_no:>2} | Page: {page_no}  Frames: {str(snapshot):<18}  [{tag}]")


def section_banner(title):
    bar = "=" * 52
    print(f"\n{bar}")
    print(f"  {title}")
    print(bar)


# ──────────────────────────────────────────────────────────
#  1.  FIFO  (First-In First-Out)
# ──────────────────────────────────────────────────────────

def run_fifo(ref_string, num_frames):
    """
    Maintains pages in arrival order using a deque.
    The page that entered memory first is evicted on a fault.
    """
    section_banner("FIFO  —  First-In, First-Out")
    page_queue = deque()          # tracks insertion order
    loaded     = set()
    fault_count = 0

    for idx, pg in enumerate(ref_string, start=1):
        fault = False
        if pg not in loaded:
            fault = True
            fault_count += 1
            if len(page_queue) == num_frames:
                evicted = page_queue.popleft()
                loaded.discard(evicted)
            page_queue.append(pg)
            loaded.add(pg)
        display_step(idx, pg, list(page_queue), fault)

    return fault_count


# ──────────────────────────────────────────────────────────
#  2.  LRU  (Least Recently Used)
# ──────────────────────────────────────────────────────────

def run_lru(ref_string, num_frames):
    """
    Tracks recency via an ordered list.
    On a hit the page moves to the tail (most-recent end).
    On a miss the head (least-recent) is evicted.
    """
    section_banner("LRU  —  Least Recently Used")
    usage_order = []    # left = LRU end, right = MRU end
    fault_count  = 0

    for idx, pg in enumerate(ref_string, start=1):
        fault = False
        if pg in usage_order:
            usage_order.remove(pg)          # refresh position
        else:
            fault = True
            fault_count += 1
            if len(usage_order) == num_frames:
                usage_order.pop(0)          # evict least-recent
        usage_order.append(pg)              # mark as most-recent
        display_step(idx, pg, usage_order, fault)

    return fault_count


# ──────────────────────────────────────────────────────────
#  3.  Optimal  (Belady / Clairvoyant)
# ──────────────────────────────────────────────────────────

def _next_use(ref_string, from_pos, page):
    """Return index of next occurrence of *page* after *from_pos*, or inf."""
    for i in range(from_pos, len(ref_string)):
        if ref_string[i] == page:
            return i
    return float("inf")


def run_optimal(ref_string, num_frames):
    """
    Looks ahead in the reference string and evicts the page
    whose next access is farthest in the future (or never).
    Theoretical lower bound — not implementable in practice.
    """
    section_banner("Optimal  —  Belady's Algorithm")
    frames      = []
    fault_count = 0

    for idx, pg in enumerate(ref_string, start=1):
        fault = False
        if pg not in frames:
            fault = True
            fault_count += 1
            if len(frames) < num_frames:
                frames.append(pg)
            else:
                # pick victim: page with the farthest next use
                victim = max(frames,
                             key=lambda p: _next_use(ref_string, idx, p))
                frames[frames.index(victim)] = pg
        display_step(idx, pg, frames, fault)

    return fault_count


# ──────────────────────────────────────────────────────────
#  4.  MRU  (Most Recently Used)
# ──────────────────────────────────────────────────────────

def run_mru(ref_string, num_frames):
    """
    Opposite of LRU — evicts the most recently accessed page.
    Performs well on cyclic sequential scans.
    """
    section_banner("MRU  —  Most Recently Used")
    frames        = []
    last_used_pos = 0       # index in frames of last accessed page
    fault_count   = 0

    for idx, pg in enumerate(ref_string, start=1):
        fault = False
        if pg in frames:
            last_used_pos = frames.index(pg)
        else:
            fault = True
            fault_count += 1
            if len(frames) < num_frames:
                frames.append(pg)
                last_used_pos = len(frames) - 1
            else:
                frames[last_used_pos] = pg
                # last_used_pos stays the same (replaced slot)
        display_step(idx, pg, frames, fault)

    return fault_count


# ──────────────────────────────────────────────────────────
#  5.  Second Chance  (Clock Algorithm)
# ──────────────────────────────────────────────────────────

def run_second_chance(ref_string, num_frames):
    """
    FIFO enhanced with a reference bit per frame.
    On a hit  → set ref-bit = 1.
    On a miss → advance clock hand, skipping pages with bit=1
                (clearing their bit); replace the first bit=0 page.
    Approximates LRU with O(1) overhead.
    """
    section_banner("Second Chance  —  Clock Algorithm")
    frames    = []
    ref_bits  = []
    hand      = 0       # clock pointer
    fault_count = 0

    for idx, pg in enumerate(ref_string, start=1):
        fault = False

        if pg in frames:
            ref_bits[frames.index(pg)] = 1      # give it a second chance
        else:
            fault = True
            fault_count += 1
            if len(frames) < num_frames:
                frames.append(pg)
                ref_bits.append(1)
            else:
                # Sweep until a page with bit=0 is found
                while ref_bits[hand] == 1:
                    ref_bits[hand] = 0
                    hand = (hand + 1) % num_frames

                frames[hand]   = pg
                ref_bits[hand] = 1
                hand = (hand + 1) % num_frames

        display_step(idx, pg, frames, fault)

    return fault_count


# ──────────────────────────────────────────────────────────
#  Summary printer
# ──────────────────────────────────────────────────────────

def print_summary(results: dict):
    bar  = "=" * 45
    sep  = "-" * 45
    best = min(results.values())
    print(f"\n{bar}")
    print(f"  {'Algorithm':<22}  {'Page Faults':>10}")
    print(sep)
    for algo, faults in results.items():
        marker = "  <-- best" if faults == best else ""
        print(f"  {algo:<22}  {faults:>10}{marker}")
    print(bar)


# ──────────────────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────────────────

def main():
    try:
        if len(sys.argv) >= 3:
            pages     = [int(x) for x in sys.argv[1].split()]
            n_frames  = int(sys.argv[2])
        else:
            raw      = input("Enter page reference string (space-separated): ")
            pages    = [int(x) for x in raw.split()]
            n_frames = int(input("Enter number of frames: "))
    except (ValueError, IndexError):
        print('Usage: python main.py "7 3 0 3 2 1 2 0 7 0 1 2" 3')
        sys.exit(1)

    scores = {}
    scores["FIFO"]          = run_fifo(pages, n_frames)
    scores["LRU"]           = run_lru(pages, n_frames)
    scores["Optimal"]       = run_optimal(pages, n_frames)
    scores["MRU"]           = run_mru(pages, n_frames)
    scores["Second Chance"] = run_second_chance(pages, n_frames)

    print_summary(scores)


if __name__ == "__main__":
    main()
