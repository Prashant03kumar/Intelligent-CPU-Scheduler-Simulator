class RoundRobin:
    def __init__(self, processes, time_quantum):
        self.processes = processes
        self.time_quantum = time_quantum

    def calculate_completion_time(self):
        queue = self.processes[:]
        current_time = 0
        timeline = []
        
        while queue:
            pid, arrival, burst = queue.pop(0)
            if current_time < arrival:
                current_time = arrival  # CPU idle time

            start_time = current_time
            executed_time = min(burst, self.time_quantum)
            end_time = start_time + executed_time
            burst -= executed_time
            timeline.append((pid, start_time, end_time))
            current_time = end_time

            if burst > 0:
                queue.append((pid, arrival, burst))  # Re-add process if remaining burst

        return timeline