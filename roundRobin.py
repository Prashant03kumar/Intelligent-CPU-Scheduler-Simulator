class RoundRobin:
    def __init__(self, processes, time_quantum):
        self.processes = processes
        self.time_quantum = time_quantum

    def calculate_completion_time(self):
        queue = self.processes[:]
        completion_time = 0
        schedule = []
        
        while queue:
            pid, arrival, burst = queue.pop(0)
            if completion_time < arrival:
                completion_time = arrival  # CPU idle time

            executed_time = min(burst, self.time_quantum)
            burst -= executed_time
            completion_time += executed_time
            schedule.append((pid, completion_time))

            if burst > 0:
                queue.append((pid, arrival, burst))  # Re-add process if remaining burst

        return schedule
