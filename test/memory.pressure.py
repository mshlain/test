"""
Memory Pressure Test Script

This script simulates an out-of-memory (OOM) condition by continuously allocating
increasing amounts of memory until the system runs out of available RAM.

Mechanism:
1. Starts by allocating a 256MB block of memory using bytearray
2. Keeps all allocated blocks in a list to prevent garbage collection
3. Doubles the size of each new allocation
4. Tracks and displays:
   - Total memory consumed (MB)
   - Time taken for each allocation


Oneliner
curl -s https://raw.githubusercontent.com/mshlain/test/refs/heads/main/test/memory.pressure.py | python3

"""

import logging
import time


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        handlers=[
            logging.FileHandler("memory.pressure.log"),
            logging.StreamHandler(),  # Keep console output
        ],
    )


def main():
    setup_logging()
    print(__doc__.strip())
    print("-" * 80)  # Add a separator line
    logging.info("")
    logging.info("Starting memory pressure test")

    size = 256 * 1024 * 1024  # Start with 256MB
    blocks = []

    while True:
        start = time.time()
        blocks.append(bytearray(size))
        size *= 2
        total_mem = sum(len(b) for b in blocks) / (1024 * 1024)
        logging.info(
            f"Memory: {total_mem:.0f}MB, Allocation time: {time.time() - start:.2f}s"
        )


if __name__ == "__main__":
    main()
