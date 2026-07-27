#!/usr/bin/env python3
import sys
import re

def parse_perf_log():
    # Read from log file or stdin
    input_data = sys.stdin.read()

    # Regex patterns
    mmap_pattern = re.compile(r'len:\s*(0x[0-9a-fA-F]+).*flags:\s*(0x[0-9a-fA-F]+)')
    brk_pattern = re.compile(r'brk:\s*(0x[0-9a-fA-F]+)')

    current_brk = 0
    mmap_bytes = 0
    brk_bytes = 0

    for line in input_data.strip().split('\n'):
        if not line or line.startswith('#'):
            continue

        # 1. Handle mmap allocations
        if "sys_enter_mmap" in line:
            mmap_match = mmap_pattern.search(line)
            if mmap_match:
                length = int(mmap_match.group(1), 16)
                flags = int(mmap_match.group(2), 16)

                # Check for MAP_ANONYMOUS (0x20). We filter out file-backed shared libraries 
                # because they don't count toward the app's unique heap consumption.
                if flags & 0x20:
                    mmap_bytes += length

        # 2. Handle brk heap movements
        elif "sys_enter_brk" in line:
            brk_match = brk_pattern.search(line)
            if brk_match:
                address = int(brk_match.group(1), 16)
                if address == 0:
                    continue
                if current_brk == 0:
                    current_brk = address  # Set baseline
                elif address > current_brk:
                    brk_bytes += (address - current_brk)
                    current_brk = address
                elif address < current_brk:
                    current_brk = address # Track reduction if heap shrinks

    total_bytes = mmap_bytes + brk_bytes
    print("=" * 45)
    print(f"APPLICATION MEMORY ANALYSIS")
    print("=" * 45)
    print(f"Heap Expansion (brk):  {brk_bytes / 1024 / 1024:.2f} MB")
    print(f"Anonymous Maps (mmap): {mmap_bytes / 1024 / 1024:.2f} MB")
    print("-" * 45)
    print(f"Total Memory Claimed:   {total_bytes / 1024 / 1024:.2f} MB ({total_bytes:,} bytes)")
    print("=" * 45)

if __name__ == '__main__':
    parse_perf_log()

