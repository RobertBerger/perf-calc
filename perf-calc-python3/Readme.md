This script parses the chronological perf script output. It tracks the shifting brk heap pointer and adds up all anonymous mmap requests to show total memory requested.

e.g.:

# Option A: Launch a specific application and record it
`perf record -e syscalls:sys_enter_brk,syscalls:sys_exit_brk,syscalls:sys_enter_mmap -- my_application`

# Option B: Attach to an already running process by PID
`perf record -e syscalls:sys_enter_brk,syscalls:sys_exit_brk,syscalls:sys_enter_mmap -p <PID> -- sleep 10`

# Generate input for perf-calc-python3
`perf script > perf_memory.log`

# run it:
`cat perf_memory.log | python3 /usr/bin/perf-calc-python3.py`
