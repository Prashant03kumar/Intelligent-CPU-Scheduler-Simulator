class RoundRobin:
    def __init__(self, processes, time_quantum):
        self.processes = processes  # List of (pid, arrival, burst)
        self.time_quantum = time_quantum

    def calculate_completion_time(self):
        # Copy processes with remaining burst time
        remaining = [(pid, arrival, burst, burst) for pid, arrival, burst in self.processes]
        # remaining format: (pid, arrival_time, original_burst, remaining_burst)
        current_time = 0
        timeline = []
        ready_queue = []

        # Sort processes by arrival time initially
        remaining.sort(key=lambda x: x[1])

        while remaining or ready_queue:
            # Add processes that have arrived to the ready queue
            while remaining and remaining[0][1] <= current_time:
                pid, arrival, burst, rem_burst = remaining.pop(0)
                ready_queue.append((pid, arrival, burst, rem_burst))

            if not ready_queue:
                # If no process is ready, move time to next arrival
                if remaining:
                    current_time = remaining[0][1]
                continue

            # Take the first process from the ready queue
            pid, arrival, burst, rem_burst = ready_queue.pop(0)
            start_time = current_time
            executed_time = min(rem_burst, self.time_quantum)
            end_time = start_time + executed_time
            rem_burst -= executed_time

            # Add to timeline
            timeline.append((pid, start_time, end_time))

            # Update current time
            current_time = end_time

            # Add newly arrived processes during this execution
            while remaining and remaining[0][1] <= current_time:
                pid_new, arrival_new, burst_new, rem_burst_new = remaining.pop(0)
                ready_queue.append((pid_new, arrival_new, burst_new, rem_burst_new))

            # If process still has remaining burst, add back to queue
            if rem_burst > 0:
                ready_queue.append((pid, arrival, burst, rem_burst))

        return timeline