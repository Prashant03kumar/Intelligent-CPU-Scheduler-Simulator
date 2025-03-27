class PriorityScheduling:
    def __init__(self, processes, is_preemptive):
        self.processes = processes  # List of (pid, at, bt, priority)
        self.is_preemptive = is_preemptive

    def add_to_ready_queue(self, processes, current_time, index, ready_queue, remaining_bt):
        """Add processes to the ready queue based on arrival time."""
        while index < len(processes) and processes[index][1] <= current_time:
            pid, _, _, priority = processes[index]
            ready_queue.append((pid, priority, remaining_bt[pid]))
            index += 1
        return index

    def _preemptive_priority(self):
        processes = sorted(self.processes, key=lambda x: x[1])
        timeline = []
        current_time = 0
        ready_queue = []
        remaining_bt = {pid: bt for pid, _, bt, _ in processes}
        completed = set()
        index = 0

        while len(completed) < len(processes):
            index = self.add_to_ready_queue(processes, current_time, index, ready_queue, remaining_bt)

            if not ready_queue:
                if index < len(processes):
                    current_time = processes[index][1]
                else:
                    break
                continue

            ready_queue.sort(key=lambda x: (-x[1], x[0]))  # Sort by priority (descending), then PID
            pid, _, _ = ready_queue.pop(0)
            start_time = current_time
            current_time += 1
            remaining_bt[pid] -= 1

            index = self.add_to_ready_queue(processes, current_time, index, ready_queue, remaining_bt)

            if remaining_bt[pid] > 0:
                ready_queue.append((pid, processes[pid-1][3], remaining_bt[pid]))
            else:
                completed.add(pid)

            timeline.append((pid, start_time, current_time))

        return timeline