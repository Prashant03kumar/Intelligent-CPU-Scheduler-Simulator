class FCFS:
    about = (
        "First Come First Serve (FCFS) Scheduling:\n\n"
        "FCFS is a non-preemptive scheduling algorithm where processes are executed in the order they arrive. "
        "The process that arrives first is allocated the CPU first, and it runs to completion before the next process starts. "
        "This algorithm is simple and fair but may lead to the convoy effect, where short processes wait behind a long process, "
        "resulting in higher average waiting times."
    )

    def __init__(self, processes):
        self.processes = processes  # List of (pid, at, bt)

    def calculate_completion_time(self):
        """Calculate completion time using FCFS scheduling."""
        processes = sorted(self.processes, key=lambda x: x[1])  # Sort by arrival time
        timeline = []
        current_time = 0

        for pid, at, bt in processes:
            # If the CPU is idle, fast-forward to the arrival time
            if current_time < at:
                current_time = at
            start_time = current_time
            current_time += bt
            timeline.append((pid, start_time, current_time))

        return timeline