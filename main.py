import os
import time
from fcfs import FCFS
from sjf import SJF
from roundRobin import RoundRobin
from priorityScheduling import PriorityScheduling

def clear_terminal():
    """Clears the terminal screen for a real-time effect."""
    os.system('cls' if os.name == 'nt' else 'clear')

def calculate_turnaround_time(at, ct):
    """Calculates Turnaround Time (TAT)."""
    return ct - at

def calculate_waiting_time(tat, bt):
    """Calculates Waiting Time (WT)."""
    return tat - bt

def display_results(processes, completion_times):
    """Updates CT one process at a time, then updates TAT & WT instantly after process completion."""
    process_ct = {pid: 0 for pid, _, _ in processes}  # Initialize CT to 0
    tat_wt_updated = set()  # Track completed processes
    time_elapsed = 0

    while True:
        clear_terminal()
        print("\n📌 Process Scheduling Results (Real-Time Execution):")
        print("────────────────────────────────────────")
        print(f"{'PID':<5}{'AT':<5}{'BT':<5}{'CT':<5}{'TAT':<5}{'WT':<5}")
        print("────────────────────────────────────────")

        all_completed = True

        for pid, at, bt in processes:
            ct_display = process_ct[pid]

            if pid in tat_wt_updated:  
                tat = calculate_turnaround_time(at, completion_times[pid])
                wt = calculate_waiting_time(tat, bt)
            else:
                tat = "-"  
                wt = "-"  

            print(f"P{pid:<4} {at:<5}{bt:<5}{ct_display:<5}{tat:<5}{wt:<5}")

        print("────────────────────────────────────────")

        # Find the first process that still needs CT updates
        for pid, at, bt in processes:
            if process_ct[pid] < completion_times[pid]:  
                process_ct[pid] += 1  # Update only one process at a time
                all_completed = False  
                break  

        # If a process just completed, update TAT & WT instantly
        for pid in process_ct:
            if process_ct[pid] == completion_times[pid] and pid not in tat_wt_updated:
                tat_wt_updated.add(pid)

        if all_completed:
            break  

        time.sleep(.1)  
        time_elapsed += 1  

def main():
    processes = [
        (1, 0, 4),  
        (2, 1, 3),
        (3, 2, 1),
        (4, 3, 5),
        (5, 4, 2)
    ]

    print("\nChoose a CPU Scheduling Algorithm:")
    print("1. First Come First Serve (FCFS)")
    print("2. Shortest Job First (SJF)")
    print("3. Round Robin (RR)")
    print("4. Priority Scheduling")

    choice = int(input("Enter choice (1-4): "))

    if choice == 1:
        scheduler = FCFS([(pid, at, bt) for pid, at, bt in processes])
    elif choice == 2:
        preemptive = input("Do you want Preemptive SJF? (yes/no): ").strip().lower() == "yes"
        scheduler = SJF([(pid, at, bt) for pid, at, bt in processes], preemptive)
    elif choice == 3:
        time_quantum = int(input("Enter Time Quantum: "))
        scheduler = RoundRobin([(pid, at, bt) for pid, at, bt in processes], time_quantum)
    elif choice == 4:
        preemptive = input("Do you want Preemptive Priority Scheduling? (yes/no): ").strip().lower() == "yes"
        scheduler = PriorityScheduling(processes, preemptive)
    else:
        print("❌ Invalid choice! Please enter a number between 1 and 4.")
        return

    schedule = scheduler.calculate_completion_time()
    completion_times = {pid: ctime for pid, ctime in schedule}

    display_results(processes, completion_times)

if __name__ == "__main__":
    main()
