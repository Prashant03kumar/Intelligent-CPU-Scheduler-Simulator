class PriorityScheduling:
    def __init__(self, processes, preemptive=False):
        self.processes = sorted(processes, key=lambda x: (x[1], x[3]))  # Sort by arrival time, then priority
        self.preemptive = preemptive

    def calculate_completion_time(self):
        if self.preemptive:
            return self._preemptive_priority()
        else:
            return self._non_preemptive_priority()

    def _non_preemptive_priority(self):
        current_time = 0
        timeline = []
        remaining_processes = self.processes.copy()

        while remaining_processes:
            available_processes = [p for p in remaining_processes if p[1] <= current_time]
            if available_processes:
                highest_priority = min(available_processes, key=lambda x: (x[3], x[1]))  
                remaining_processes.remove(highest_priority)
                start_time = current_time
                end_time = start_time + highest_priority[2]
                timeline.append((highest_priority[0], start_time, end_time))
                current_time = end_time
            else:
                current_time += 1  # CPU idle
        
        return timeline

    def _preemptive_priority(self):
        current_time = 0
        timeline = []
        remaining_processes = {p[0]: [p[1], p[2], p[3]] for p in self.processes}  # {PID: [Arrival Time, Remaining Burst, Priority]}
        current_pid = None
        start_time = None

        while remaining_processes:
            available_processes = {pid: info for pid, info in remaining_processes.items() if info[0] <= current_time}
            if available_processes:
                highest_priority = min(available_processes, key=lambda x: (available_processes[x][2], available_processes[x][0]))
                if current_pid != highest_priority:
                    if current_pid is not None:
                        timeline.append((current_pid, start_time, current_time))
                    current_pid = highest_priority
                    start_time = current_time
                remaining_processes[highest_priority][1] -= 1
                current_time += 1
                if remaining_processes[highest_priority][1] == 0:
                    timeline.append((current_pid, start_time, current_time))
                    current_pid = None
                    start_time = None
                    del remaining_processes[highest_priority]
            else:
                if current_pid is not None:
                    timeline.append((current_pid, start_time, current_time))
                    current_pid = None
                    start_time = None
                current_time += 1
        
        return timeline