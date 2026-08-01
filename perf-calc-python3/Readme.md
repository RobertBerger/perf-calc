This script parses the chronological perf script output.

e.g.:

# Option A: Launch a specific application and record it
`perf record -e syscalls:sys_enter_mmap -e syscalls:sys_enter_mprotect -e syscalls:sys_exit_brk -- ./my_application`

# Option B: Attach to an already running process by PID
`perf record -e syscalls:sys_enter_mmap -e syscalls:sys_enter_mprotect -e syscalls:sys_exit_brk -p <PID> -- sleep 10`

# Generate input for perf-calc-python3
`perf script > perf_memory.log`

# run it:
`cat perf_memory.log | python3 /usr/bin/perf-calc-python3.py`
