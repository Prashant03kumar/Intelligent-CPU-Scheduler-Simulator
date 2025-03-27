class RoundRobin:
    def __init__(self, processes, time_quantum):
        self.processes = processes
        self.time_quantum = time_quantum

    def add_to_ready_queue(self, processes, current_time, index, ready_queue):
        """Add processes to the ready queue based on arrival time."""
        while index < len(processes) and processes[index][1] <= current_time:
            pid, _, _ = processes[index]
            ready_queue.append(pid)
            index += 1
        return index

    def calculate_completion_time(self):
        processes = sorted(self.processes, key=lambda x: x[1])
        timeline = []
        current_time = 0
        ready_queue = []
        remaining_bt = {pid: bt for pid, _, bt in processes}
        completed = set()
        index = 0

        while len(completed) < len(processes):
            # Add arriving processes to the ready queue
            index = self.add_to_ready_queue(processes, current_time, index, ready_queue)

            if not ready_queue:
                if index < len(processes):
                    current_time = processes[index][1]
                else:
                    break
                continue

            pid = ready_queue.pop(0)
            start_time = current_time
            execution_time = min(self.time_quantum, remaining_bt[pid])
            current_time += execution_time
            remaining_bt[pid] -= execution_time

            # Add processes that arrived during execution
            index = self.add_to_ready_queue(processes, current_time, index, ready_queue)

            if remaining_bt[pid] > 0:
                ready_queue.append(pid)
            else:
                completed.add(pid)

            timeline.append((pid, start_time, current_time))

        return timeline