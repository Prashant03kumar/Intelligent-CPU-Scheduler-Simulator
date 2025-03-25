class FCFS:
    def __init__(self, processes):
        self.processes = sorted(processes, key=lambda x: x[1])  # Sort by arrival time

    def calculate_completion_time(self):
        current_time = 0
        timeline = []
        
        for pid, arrival, burst in self.processes:
            if current_time < arrival:
                current_time = arrival  # Wait if CPU is idle
            start_time = current_time
            end_time = start_time + burst
            timeline.append((pid, start_time, end_time))
            current_time = end_time
        
        return timeline