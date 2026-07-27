#!/usr/bin/env python3
import sys
import re

def parse_accurate_perf():
    input_data = sys.stdin.read()
    
    # Regex for mmap lengths
    mmap_pattern = re.compile(r'len:\s*(0x[0-9a-fA-F]+).*flags:\s*(0x[0-9a-fA-F]+)')
    # Regex for tracking the return value of the brk exit system call
    exit_brk_pattern = re.compile(r'sys_exit_brk:\s*0x([0-9a-fA-F]+)')
    
    current_brk = 0
    brk_bytes = 0
    mmap_bytes = 0
    
    for line in input_data.strip().split('\n'):
        if not line or line.startswith('#'):
            continue
            
        # 1. Handle mmap entries (same as before, filtering for anonymous maps)
        if "sys_enter_mmap" in line:
            mmap_match = mmap_pattern.search(line)
            if mmap_match:
                length = int(mmap_match.group(1), 16)
                flags = int(mmap_match.group(2), 16)
                if flags & 0x20:  # MAP_ANONYMOUS
                    mmap_bytes += length

        # 2. Handle actual kernel-approved brk changes
        elif "sys_exit_brk" in line:
            exit_match = exit_brk_pattern.search(line)
            if exit_match:
                # The kernel returns the actual valid address pointer here
                actual_address = int(exit_match.group(1), 16)
                
                if current_brk == 0:
                    current_brk = actual_address  # Set our true baseline
                    continue
                
                if actual_address > current_brk:
                    diff = actual_address - current_brk
                    brk_bytes += diff
                    current_brk = actual_address
                elif actual_address < current_brk:
                    # Heap shrank / freed memory
                    current_brk = actual_address

    total_bytes = mmap_bytes + brk_bytes
    print("=" * 45)
    print(f"ACCURATE MEMORY ANALYSIS (EXIT-TRACKED)")
    print("=" * 45)
    print(f"True Heap Growth (brk):  {brk_bytes / 1024 / 1024:.2f} MB")
    print(f"Anonymous Maps (mmap):   {mmap_bytes / 1024 / 1024:.2f} MB")
    print("-" * 45)
    print(f"Total Unique Memory:     {total_bytes / 1024 / 1024:.2f} MB")
    print("=" * 45)

if __name__ == '__main__':
    parse_accurate_perf()

