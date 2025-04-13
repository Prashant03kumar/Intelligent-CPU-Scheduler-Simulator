class PriorityScheduling:
    about = {
        "preemptive": (
            "Priority Scheduling (Preemptive):\n\n"
            "In preemptive Priority Scheduling, each process is assigned a priority (lower number indicates higher priority), "
            "and the CPU is allocated to the highest-priority process that has arrived. If a higher-priority process arrives, "
            "the current process is preempted, and the new process takes over. This ensures critical tasks are handled promptly but "
            "may cause starvation for low-priority processes if high-priority processes keep arriving."
        ),
        "non_preemptive": (
            "Priority Scheduling (Non-Preemptive):\n\n"
            "In non-preemptive Priority Scheduling, the CPU is allocated to the highest-priority process among those that have "
            "arrived, and it runs to completion without interruption. Priorities are represented by numbers, with lower numbers "
            "indicating higher priority. This algorithm prioritizes important tasks but may lead to longer waiting times for "
            "low-priority processes."
        )
    }

    def __init__(self, processes, is_preemptive):
        print("Initializing PriorityScheduling with processes:", processes, "is_preemptive:", is_preemptive)
        self.processes = sorted(processes, key=lambda x: x[1])  # Sort by arrival time
        self.is_preemptive = is_preemptive
        self.timeline = []

    def calculate_preemptive(self, process_list):
        print("Starting preemptive scheduling with process_list:", process_list)
        current_time = 0
        completed = 0
        n = len(process_list)
        ready_queue = []
        prev_pid = None
        start_time = 0
        timeline = []

        while completed < n:
            print(f"Time {current_time}, Completed: {completed}/{n}")
            # Add processes to the ready queue that have arrived by current_time
            for i, (pid, at, bt, priority, remaining_bt, idx) in enumerate(process_list):
                if at <= current_time and remaining_bt > 0 and (pid, i) not in [(p[0], p[1]) for p in ready_queue]:
                    ready_queue.append((pid, i, priority, remaining_bt, idx))
            print("Ready queue:", ready_queue)

            if not ready_queue:
                current_time += 1
                continue

            # Sort ready queue by priority (lower priority number = higher priority)
            # If priorities are equal, use original index (earlier arrival time) as tiebreaker
            ready_queue.sort(key=lambda x: (x[2], x[4]))
            current_pid, idx, priority, remaining_bt, _ = ready_queue[0]
            print(f"Selected process: PID={current_pid}, Priority={priority}, Remaining BT={remaining_bt}")

            # Skip processes with zero burst time
            if process_list[idx][2] == 0:  # Original burst time is 0
                process_list[idx] = (current_pid, process_list[idx][1], process_list[idx][2], priority, 0, idx)
                completed += 1
                ready_queue.pop(0)
                if prev_pid == current_pid:
                    timeline.append((current_pid, current_time, current_time))
                    prev_pid = None
                continue

            # Execute for 1 time unit
            new_remaining_bt = process_list[idx][4] - 1
            process_list[idx] = (current_pid, process_list[idx][1], process_list[idx][2], priority, new_remaining_bt, idx)
            
            # Update the timeline
            if prev_pid != current_pid:
                if prev_pid is not None:
                    timeline.append((prev_pid, start_time, current_time))
                start_time = current_time
            prev_pid = current_pid

            # Remove the process from the ready queue (it will be re-added in the next iteration with updated remaining_bt)
            ready_queue.pop(0)

            current_time += 1

            if new_remaining_bt == 0:  # Process completed
                completed += 1
                if prev_pid == current_pid:
                    timeline.append((current_pid, start_time, current_time))
                    prev_pid = None

        print("Preemptive timeline:", timeline)
        return timeline

    def calculate_non_preemptive(self, process_list):
        print("Starting non-preemptive scheduling with process_list:", process_list)
        current_time = 0
        completed = 0
        n = len(process_list)
        ready_queue = []
        timeline = []

        while completed < n:
            print(f"Time {current_time}, Completed: {completed}/{n}")
            # Add processes to the ready queue that have arrived by current_time
            for i, (pid, at, bt, priority, remaining_bt, idx) in enumerate(process_list):
                if at <= current_time and remaining_bt > 0 and (pid, i) not in [(p[0], p[1]) for p in ready_queue]:
                    ready_queue.append((pid, i, priority, remaining_bt, idx))
            print("Ready queue:", ready_queue)

            if not ready_queue:
                current_time += 1
                continue

            # Sort ready queue by priority (lower priority number = higher priority)
            # If priorities are equal, use original index (earlier arrival time) as tiebreaker
            ready_queue.sort(key=lambda x: (x[2], x[4]))
            current_pid, idx, priority, remaining_bt, _ = ready_queue[0]
            print(f"Selected process: PID={current_pid}, Priority={priority}, Remaining BT={remaining_bt}")

            # Skip processes with zero burst time
            if process_list[idx][2] == 0:  # Original burst time is 0
                process_list[idx] = (current_pid, process_list[idx][1], process_list[idx][2], priority, 0, idx)
                completed += 1
                ready_queue.pop(0)
                timeline.append((current_pid, current_time, current_time))
                continue

            # Execute the process to completion
            process_list[idx] = (current_pid, process_list[idx][1], process_list[idx][2], priority, 0, idx)
            start_time = current_time
            current_time += remaining_bt
            timeline.append((current_pid, start_time, current_time))
            completed += 1
            ready_queue.pop(0)

        print("Non-preemptive timeline:", timeline)
        return timeline

    def calculate_completion_time(self):
        if not self.processes:
            return []

        # Create a list of processes with remaining burst time and original index for tiebreaking
        process_list = [(pid, at, bt, priority, bt, idx) for idx, (pid, at, bt, priority) in enumerate(self.processes)]

        if self.is_preemptive:
            self.timeline = self.calculate_preemptive(process_list)
        else:
            self.timeline = self.calculate_non_preemptive(process_list)

        return self.timeline