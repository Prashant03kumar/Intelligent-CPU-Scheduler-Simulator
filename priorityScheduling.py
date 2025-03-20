class PriorityScheduling:
    def __init__(self, processes, preemptive=False):
        """
        :param processes: List of tuples (PID, Arrival Time, Burst Time, Priority)
        :param preemptive: Boolean flag for Preemptive or Non-Preemptive Priority Scheduling
        """
        self.processes = sorted(processes, key=lambda x: (x[1], x[3]))  # Sort by arrival time, then priority
        self.preemptive = preemptive

    def calculate_completion_time(self):
        if self.preemptive:
            return self._preemptive_priority()
        else:
            return self._non_preemptive_priority()

    def _non_preemptive_priority(self):
        """Non-preemptive Priority Scheduling"""
        completion_time = 0
        schedule = []
        remaining_processes = self.processes.copy()

        while remaining_processes:
            # Get processes that have arrived
            available_processes = [p for p in remaining_processes if p[1] <= completion_time]
            if available_processes:
                # Sort by priority first, then FCFS (arrival time)
                highest_priority = min(available_processes, key=lambda x: (x[3], x[1]))  
                remaining_processes.remove(highest_priority)
                completion_time += highest_priority[2]  # Execute process
                schedule.append((highest_priority[0], completion_time))
            else:
                completion_time += 1  # CPU idle
        
        return schedule

    def _preemptive_priority(self):
        """Preemptive Priority Scheduling"""
        completion_time = 0
        schedule = []
        remaining_processes = {p[0]: [p[1], p[2], p[3]] for p in self.processes}  # {PID: [Arrival Time, Remaining Burst, Priority]}
        executed_processes = []

        while remaining_processes:
            # Get processes that have arrived
            available_processes = {pid: info for pid, info in remaining_processes.items() if info[0] <= completion_time}
            if available_processes:
                # Sort by priority first, then FCFS (arrival time)
                highest_priority = min(available_processes, key=lambda x: (available_processes[x][2], available_processes[x][0]))
                
                remaining_processes[highest_priority][1] -= 1  # Reduce remaining burst time
                completion_time += 1  # Increment time
                executed_processes.append(highest_priority)

                if remaining_processes[highest_priority][1] == 0:  # Process completes execution
                    schedule.append((highest_priority, completion_time))
                    del remaining_processes[highest_priority]
            else:
                completion_time += 1  # CPU idle
        
        return schedule
