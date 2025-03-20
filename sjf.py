class SJF:
    def __init__(self, processes, preemptive=False):
        """
        :param processes: List of tuples (PID, Arrival Time, Burst Time)
        :param preemptive: Boolean flag for Preemptive (SRTF) or Non-Preemptive SJF
        """
        self.processes = sorted(processes, key=lambda x: (x[1], x[2]))  # Sort by arrival, then burst
        self.preemptive = preemptive

    def calculate_completion_time(self):
        if self.preemptive:
            return self._preemptive_sjf()
        else:
            return self._non_preemptive_sjf()

    def _non_preemptive_sjf(self):
        """Non-preemptive SJF (Shortest Job First)"""
        completion_time = 0
        schedule = []
        remaining_processes = self.processes.copy()

        while remaining_processes:
            available_processes = [p for p in remaining_processes if p[1] <= completion_time]
            if available_processes:
                shortest = min(available_processes, key=lambda x: x[2])  # Choose the shortest burst time
                remaining_processes.remove(shortest)
                completion_time += shortest[2]
                schedule.append((shortest[0], completion_time))
            else:
                completion_time += 1  # CPU idle
        
        return schedule

    def _preemptive_sjf(self):
        """Preemptive SJF (Shortest Remaining Time First - SRTF)"""
        completion_time = 0
        schedule = []
        remaining_processes = {p[0]: [p[1], p[2]] for p in self.processes}  # {PID: [Arrival Time, Remaining Burst]}
        executed_processes = []

        while remaining_processes:
            available_processes = {pid: info for pid, info in remaining_processes.items() if info[0] <= completion_time}
            if available_processes:
                # Select process with the shortest remaining time
                shortest = min(available_processes, key=lambda x: available_processes[x][1])
                remaining_processes[shortest][1] -= 1  # Reduce remaining burst time
                completion_time += 1  # Increment time
                executed_processes.append(shortest)

                if remaining_processes[shortest][1] == 0:  # Process completes execution
                    schedule.append((shortest, completion_time))
                    del remaining_processes[shortest]
            else:
                completion_time += 1  # CPU idle
        
        return schedule
