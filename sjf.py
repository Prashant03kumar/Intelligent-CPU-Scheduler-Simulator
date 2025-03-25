class SJF:
    def __init__(self, processes, preemptive=False):
        self.processes = sorted(processes, key=lambda x: (x[1], x[2]))  # Sort by arrival, then burst
        self.preemptive = preemptive

    def calculate_completion_time(self):
        if self.preemptive:
            return self._preemptive_sjf()
        else:
            return self._non_preemptive_sjf()

    def _non_preemptive_sjf(self):
        current_time = 0
        timeline = []
        remaining_processes = self.processes.copy()

        while remaining_processes:
            available_processes = [p for p in remaining_processes if p[1] <= current_time]
            if available_processes:
                shortest = min(available_processes, key=lambda x: x[2])  # Shortest burst time
                remaining_processes.remove(shortest)
                start_time = current_time
                end_time = start_time + shortest[2]
                timeline.append((shortest[0], start_time, end_time))
                current_time = end_time
            else:
                current_time += 1  # CPU idle
        
        return timeline

    def _preemptive_sjf(self):
        current_time = 0
        timeline = []
        remaining_processes = {p[0]: [p[1], p[2]] for p in self.processes}  # {PID: [Arrival Time, Remaining Burst]}
        current_pid = None
        start_time = None

        while remaining_processes:
            available_processes = {pid: info for pid, info in remaining_processes.items() if info[0] <= current_time}
            if available_processes:
                shortest = min(available_processes, key=lambda x: available_processes[x][1])
                if current_pid != shortest:
                    if current_pid is not None:
                        timeline.append((current_pid, start_time, current_time))
                    current_pid = shortest
                    start_time = current_time
                remaining_processes[shortest][1] -= 1
                current_time += 1
                if remaining_processes[shortest][1] == 0:
                    timeline.append((current_pid, start_time, current_time))
                    current_pid = None
                    start_time = None
                    del remaining_processes[shortest]
            else:
                if current_pid is not None:
                    timeline.append((current_pid, start_time, current_time))
                    current_pid = None
                    start_time = None
                current_time += 1
        
        return timeline