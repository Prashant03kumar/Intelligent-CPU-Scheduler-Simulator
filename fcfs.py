class FCFS:
    def __init__(self, processes):
        self.processes = sorted(processes, key=lambda x: x[1])  # Sort by arrival time

    def calculate_completion_time(self):
        completion_time = 0
        schedule = []
        
        for pid, arrival, burst in self.processes:
            if completion_time < arrival:
                completion_time = arrival  # Wait if CPU is idle
            completion_time += burst
            schedule.append((pid, completion_time))
        
        return schedule
class FCFS:
    def __init__(self, processes):
        self.processes = sorted(processes, key=lambda x: x[1])  # Sort by arrival time

    def calculate_completion_time(self):
        completion_time = 0
        schedule = []
        
        for pid, arrival, burst in self.processes:
            if completion_time < arrival:
                completion_time = arrival  # Wait if CPU is idle
            completion_time += burst
            schedule.append((pid, completion_time))
        
        return schedule
class FCFS:
    def __init__(self, processes):
        self.processes = sorted(processes, key=lambda x: x[1])  # Sort by arrival time

    def calculate_completion_time(self):
        completion_time = 0
        schedule = []
        
        for pid, arrival, burst in self.processes:
            if completion_time < arrival:
                completion_time = arrival  # Wait if CPU is idle
            completion_time += burst
            schedule.append((pid, completion_time))
        
        return schedule
