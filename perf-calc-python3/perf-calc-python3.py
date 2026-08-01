#!/usr/bin/env python3
import sys
import re

def parse_accurate_perf():
    input_data = sys.stdin.read()
    
    # Updated Regex to capture length, prot, and flags from mmap
    # Expects format: ... len: 0x..., prot: 0x..., flags: 0x...
    mmap_pattern = re.compile(r'len:\s*(0x[0-9a-fA-F]+).*prot:\s*(0x[0-9a-fA-F]+).*flags:\s*(0x[0-9a-fA-F]+)')
    # Regex for mprotect tracking
    mprotect_pattern = re.compile(r'len:\s*(0x[0-9a-fA-F]+).*prot:\s*(0x[0-9a-fA-F]+)')
    # Regex for tracking the return value of the brk exit system call
    exit_brk_pattern = re.compile(r'sys_exit_brk:\s*0x([0-9a-fA-F]+)')
    
    current_brk = 0
    brk_bytes = 0
    mmap_active_bytes = 0
    mmap_virtual_only_bytes = 0
    mprotect_activated_bytes = 0
    
    for line in input_data.strip().split('\n'):
        if not line or line.startswith('#'):
            continue
            
        # 1. Handle mmap entries (checking protection flags)
        if "sys_enter_mmap" in line:
            mmap_match = mmap_pattern.search(line)
            if mmap_match:
                length = int(mmap_match.group(1), 16)
                prot = int(mmap_match.group(2), 16)
                flags = int(mmap_match.group(3), 16)
                
                if flags & 0x20:  # MAP_ANONYMOUS
                    # If prot is PROT_NONE (0x0), it's just a virtual reservation
                    if prot == 0:
                        mmap_virtual_only_bytes += length
                    else:
                        # Memory is readable/writable, kernel will allocate physical pages
                        mmap_active_bytes += length

        # 2. Handle mprotect (Virtual memory turning into real active memory)
        elif "sys_enter_mprotect" in line:
            mprotect_match = mprotect_pattern.search(line)
            if mprotect_match:
                length = int(mprotect_match.group(1), 16)
                prot = int(mprotect_match.group(2), 16)
                # If Go is changing protection to Read/Write (0x1, 0x2, or 0x3)
                if prot & 0x3:
                    mprotect_activated_bytes += length

        # 3. Handle actual kernel-approved brk changes
        elif "sys_exit_brk" in line:
            exit_match = exit_brk_pattern.search(line)
            if exit_match:
                actual_address = int(exit_match.group(1), 16)
                
                if current_brk == 0:
                    current_brk = actual_address  
                    continue
                
                if actual_address > current_brk:
                    diff = actual_address - current_brk
                    brk_bytes += diff
                    current_brk = actual_address
                elif actual_address < current_brk:
                    current_brk = actual_address

    # Total physical footprint is active mmaps + mprotect activations + heap growth
    true_physical_ram = mmap_active_bytes + mprotect_activated_bytes + brk_bytes
    
    print("=" * 45)
    print(f"REAL EMBEDDED MEMORY ANALYSIS")
    print("=" * 45)
    print(f"True Heap Growth (brk):       {brk_bytes / 1024 / 1024:.2f} MB")
    print(f"Immediate Active Maps:        {mmap_active_bytes / 1024 / 1024:.2f} MB")
    print(f"Activated via mprotect:       {mprotect_activated_bytes / 1024 / 1024:.2f} MB")
    print("-" * 45)
    print(f"ESTIMATED REAL RAM USAGE:     {true_physical_ram / 1024 / 1024:.2f} MB")
    print("=" * 45)
    print(f"Ignored Virtual Space:        {mmap_virtual_only_bytes / 1024 / 1024:.2f} MB")
    print("=" * 45)

if __name__ == '__main__':
    parse_accurate_perf()

