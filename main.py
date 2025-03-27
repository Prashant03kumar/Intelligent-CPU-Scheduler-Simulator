import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, 
                            QMainWindow, QHBoxLayout, QSpinBox, QPushButton, 
                            QMessageBox, QProgressBar)
from PyQt5.QtGui import QFont, QPainter, QColor
from PyQt5.QtCore import Qt, QTimer

from fcfs import FCFS
from sjf import SJF
from roundRobin import RoundRobin
from priorityScheduling import PriorityScheduling

# Backend functions
def calculate_turnaround_time(at, ct):
    return ct - at

def calculate_waiting_time(tat, bt):
    return tat - bt

class GanttChart(QWidget):
    def __init__(self, timeline, processes, max_time):
        super().__init__()
        self.timeline = timeline
        self.processes = processes 
        self.max_time = max_time
        self.setMinimumSize(600, 120)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(QFont("Arial", 10))
        width = self.width()
        height = self.height()
        row_height = height // max(1, len(self.processes))
        time_scale = width / max(1, self.max_time)

        painter.fillRect(self.rect(), QColor(255, 255, 255))

        colors = [QColor(255, 100, 100), QColor(100, 255, 100), 
                 QColor(100, 100, 255), QColor(255, 255, 100), 
                 QColor(255, 100, 255)]

        if self.timeline:
            for pid, start, end in self.timeline:
                row = self.processes.index(pid)
                y = row * row_height
                x_start = start * time_scale
                x_width = (end - start) * time_scale
                color = colors[row % len(colors)]
                painter.fillRect(int(x_start), y, int(x_width), row_height - 5, color)
                painter.drawText(int(x_start) + 5, y + row_height // 2, f"P{pid}")

        for t in range(self.max_time + 1):
            x = t * time_scale
            painter.drawLine(int(x), 0, int(x), height)
            painter.drawText(int(x), height - 15, str(t))

class InnerWindow(QMainWindow):
    def __init__(self, algorithm_choice, process_quantity, is_preemptive, time_quantum):
        super().__init__()
        self.algorithm_choice = algorithm_choice
        self.process_quantity = process_quantity
        self.is_preemptive = is_preemptive
        self.time_quantum = time_quantum
        self.processes = []
        self.initUI()
    
    def initUI(self):
        self.setup_window_basics()
        self.layout = QVBoxLayout(self.centralWidget)

        self.subMainLayout1 = QVBoxLayout()
        self.setup_top_section()
        self.subMainLayout1.addStretch()

        self.subMainLayout2 = QVBoxLayout()
        self.setup_process_table()

        self.subMainLayout2_5 = QVBoxLayout()
        self.setup_gantt_chart()

        self.subMainLayout3 = QVBoxLayout()
        self.setup_averages_section()

        self.subMainLayout4 = QHBoxLayout()
        self.setup_ready_queue_and_buttons()

        self.layout.addLayout(self.subMainLayout1)
        self.layout.addLayout(self.subMainLayout2)
        self.layout.addLayout(self.subMainLayout2_5)
        self.layout.addStretch()
        self.layout.addLayout(self.subMainLayout3)
        self.layout.addLayout(self.subMainLayout4)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_execution)

    def setup_window_basics(self):
        self.setWindowTitle("Algorithm Execution")
        self.setGeometry(100, 100, 900, 700)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setStyleSheet("""
            background-image: url('src/photo.jpeg');
            background-repeat: no-repeat;
            background-position: center;
        """)

    def setup_top_section(self):
        self.top_Layout = QVBoxLayout()

        self.algo_Layout = QHBoxLayout()
        self.label = QLabel("Algorithm:")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setStyleSheet("color: yellow; background: transparent;")
        self.algo_Layout.addWidget(self.label)

        if self.algorithm_choice == "Round Robin (RR)":
            self.is_preemptive = True

        algo_text = f"{self.algorithm_choice}{' (Preemptive)' if self.is_preemptive else ' (Non-Preemptive)'}"
        self.algo_label = QLabel(algo_text)
        font = QFont()
        font.setPointSize(12)
        self.algo_label.setFont(font)
        self.algo_label.setAlignment(Qt.AlignLeft)
        self.algo_label.setStyleSheet("color: white; background: black;")
        self.algo_Layout.addWidget(self.algo_label)
        self.algo_Layout.addStretch()

        self.cpu_Layout = QHBoxLayout()
        self.label = QLabel("CPU:")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setStyleSheet("color: yellow; background: transparent;")
        self.cpu_Layout.addWidget(self.label)
        self.cpu_Layout.addSpacing(60)

        self.cpu_label = QLabel(" Idle ")
        font = QFont()
        font.setPointSize(12)
        self.cpu_label.setFont(font)
        self.cpu_label.setAlignment(Qt.AlignCenter)
        self.cpu_label.setStyleSheet("color: white; background: black;")
        self.cpu_Layout.addWidget(self.cpu_label)
        self.cpu_Layout.addStretch()

        self.top_Layout.addLayout(self.algo_Layout)
        self.top_Layout.addLayout(self.cpu_Layout)
        self.top_Layout.addStretch()
        self.subMainLayout1.addLayout(self.top_Layout)

    def setup_process_table(self):
        self.processTableLayout = QHBoxLayout()
        self.processTableContent = QVBoxLayout()

        self.heading = QVBoxLayout()
        self.column = QHBoxLayout()

        headers = ["Priority", "Processes", "AT", "BT", "Status Bar", "CT", "TAT", "WT"]
        for title in headers:
            label = QLabel(title)
            font = QFont()
            font.setPointSize(13)
            font.setBold(True)
            label.setFont(font)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: yellow; background: transparent;")
            label.setFixedWidth(90 if title in ["Priority", "AT", "BT"] else 110)
            self.column.addWidget(label)

        self.heading.addLayout(self.column)
        self.processTableContent.addLayout(self.heading)

        self.content = QVBoxLayout()
        self.processes_data = []

        for i in range(1, self.process_quantity + 1):
            process_row = self.create_process_row(i)
            self.content.addLayout(process_row)

        self.processTableContent.addLayout(self.content)
        self.processTableLayout.addLayout(self.processTableContent)
        self.subMainLayout2.addLayout(self.processTableLayout)

    def create_spin_box(self, min_val, max_val, value, width, height, font_size=13):
        """Create a styled QSpinBox."""
        spin_box = QSpinBox()
        spin_box.setRange(min_val, max_val)
        spin_box.setValue(value)
        spin_box.setStyleSheet("color: black; background: white;")
        spin_box.setFixedWidth(width)
        spin_box.setFixedHeight(height)
        spin_box.setFont(QFont("Arial", font_size))
        spin_box.setAlignment(Qt.AlignCenter)
        return spin_box

    def create_label(self, text, width, font_size=13, style="color: white; background: transparent;"):
        """Create a styled QLabel."""
        label = QLabel(text)
        label.setFont(QFont("Arial", font_size))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(style)
        label.setFixedWidth(width)
        return label

    def create_progress_bar(self, width, height):
        """Create a styled QProgressBar."""
        status_bar = QProgressBar()
        status_bar.setMaximum(100)
        status_bar.setValue(0)
        status_bar.setStyleSheet("QProgressBar { background-color: white; } QProgressBar::chunk { background-color: orange; }")
        status_bar.setFixedWidth(width)
        status_bar.setFixedHeight(height)
        status_bar.setAlignment(Qt.AlignCenter)
        return status_bar

    def create_process_row(self, i):
        process_row = QHBoxLayout()

        priority_input = self.create_spin_box(0, 100, 0, 90, 30)
        process_row.addWidget(priority_input)

        process_label = self.create_label(f"P{i}", 110)
        process_row.addWidget(process_label)

        at_input = self.create_spin_box(0, 100, 0, 90, 30)
        process_row.addWidget(at_input)

        bt_input = self.create_spin_box(1, 1000, 0, 90, 30)
        process_row.addWidget(bt_input)

        status_bar = self.create_progress_bar(110, 30)
        process_row.addWidget(status_bar)

        ct_label = self.create_label("0", 120)
        tat_label = self.create_label("0", 120)
        waiting_time_label = self.create_label("0", 120)
        process_row.addWidget(ct_label)
        process_row.addWidget(tat_label)
        process_row.addWidget(waiting_time_label)

        self.processes_data.append({
            "priority": priority_input,
            "at": at_input,
            "bt": bt_input,
            "status_bar": status_bar,
            "ct": ct_label,
            "tat": tat_label,
            "waiting_time": waiting_time_label,
            "remaining_bt": 0,
            "current_ct": 0,
            "slices": [],
            "completed": False
        })

        return process_row

    def setup_gantt_chart(self):
        self.gantt_label = QLabel("Gantt Chart:")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.gantt_label.setFont(font)
        self.gantt_label.setAlignment(Qt.AlignLeft)
        self.gantt_label.setStyleSheet("color: yellow; background: transparent;")
        self.subMainLayout2_5.addWidget(self.gantt_label)

        self.gantt_widget = GanttChart([], [], 0)
        self.subMainLayout2_5.addWidget(self.gantt_widget)

    def create_metric_layout(self, label_text, value_text, spacing=0):
        """Create a horizontal layout with a label and value for a metric."""
        layout = QHBoxLayout()
        label = QLabel(label_text)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        label.setFont(font)
        label.setAlignment(Qt.AlignLeft)
        label.setStyleSheet("color: yellow; background: transparent;")
        layout.addWidget(label)
        if spacing:
            layout.addSpacing(spacing)

        value_label = QLabel(value_text)
        font = QFont("Arial", 12)
        value_label.setFont(font)
        value_label.setAlignment(Qt.AlignLeft)
        value_label.setStyleSheet("color: white; background: transparent;" if label_text != "Time Quantum: " else "color: white; background: black;")
        layout.addWidget(value_label)
        layout.addStretch()
        return layout, value_label

    def setup_averages_section(self):
        self.averageContainer = QWidget()
        self.averageContainer.setFixedHeight(135)
        self.averageContainer.setStyleSheet("background: transparent;")
        self.average_layout = QVBoxLayout(self.averageContainer)

        if self.algorithm_choice == "Round Robin (RR)":
            time_quantum_layout, self.timeQuantum_value = self.create_metric_layout("Time Quantum: ", str(self.time_quantum))
            self.average_layout.addLayout(time_quantum_layout)

        waiting_time_layout, self.avgWtTime = self.create_metric_layout("Average Waiting Time: ", "0", spacing=40)
        turnaround_time_layout, self.avgTaTime = self.create_metric_layout("Average Turnaround Time: ", "0")
        total_exec_time_layout, self.totalExecTime = self.create_metric_layout("Total Execution Time: ", "0", spacing=55)

        self.average_layout.addLayout(waiting_time_layout)
        self.average_layout.addLayout(turnaround_time_layout)
        self.average_layout.addLayout(total_exec_time_layout)
        self.subMainLayout3.addWidget(self.averageContainer, alignment=Qt.AlignLeft)

    def create_styled_button(self, text, slot):
        """Helper method to create a styled QPushButton."""
        button = QPushButton(text)
        button.setFixedSize(100, 35)
        font = QFont("Arial", 10)
        font.setBold(True)
        button.setFont(font)
        button.setStyleSheet("color: black; background: white;")
        button.clicked.connect(slot)
        return button

    def exit_application(self):
        """Slot to exit the application."""
        QApplication.quit()

    def setup_ready_queue_and_buttons(self):
        self.readyQueueContainer = QWidget()
        self.readyQueueContainer.setFixedHeight(60)
        self.readyQueueContainer.setStyleSheet("background: transparent;")
        self.readQueue_layout = QHBoxLayout(self.readyQueueContainer)

        self.label = QLabel("Ready Queue: ")
        font = QFont()
        font.setPointSize(12)
        font.setItalic(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setStyleSheet("color: white; background: transparent;")
        self.label.setFixedWidth(120)
        self.readQueue_layout.addWidget(self.label)
        self.readQueue_layout.addSpacing(20)

        self.ready_queue_display = QLabel("Empty")
        font = QFont("Arial", 12)
        self.ready_queue_display.setFont(font)
        self.ready_queue_display.setAlignment(Qt.AlignLeft)
        self.ready_queue_display.setStyleSheet("color: white; background: black; padding: 5px;")
        self.readQueue_layout.addWidget(self.ready_queue_display)
        self.readQueue_layout.addStretch()

        self.subMainLayout4.addWidget(self.readyQueueContainer)
        self.subMainLayout4.addStretch()

        self.compile_btn = self.create_styled_button("Compile", self.compileSimulation)
        self.subMainLayout4.addWidget(self.compile_btn)

        self.home_btn = self.create_styled_button("Home", self.return_to_main)
        self.subMainLayout4.addWidget(self.home_btn)

        self.exit_btn = self.create_styled_button("Exit", self.exit_application)
        self.subMainLayout4.addWidget(self.exit_btn)

    def return_to_main(self):
        """Return to the main CPUScheduler window and close the current window."""
        self.main_window = CPUScheduler()
        self.main_window.show()
        self.close()

    def get_scheduler(self):
        """Return the appropriate scheduler based on the algorithm choice."""
        schedulers = {
            "First Come First Serve (FCFS)": lambda: FCFS([(pid, at, bt) for pid, at, bt, _ in self.processes]),
            "Shortest Job First (SJF)": lambda: SJF([(pid, at, bt) for pid, at, bt, _ in self.processes], self.is_preemptive),
            "Round Robin (RR)": lambda: RoundRobin([(pid, at, bt) for pid, at, bt, _ in self.processes], self.time_quantum),
            "Priority Scheduling": lambda: PriorityScheduling(self.processes, self.is_preemptive)
        }
        return schedulers[self.algorithm_choice]()

    def initialize_processes(self):
        """Initialize the processes list and reset process data."""
        self.processes = []
        for i, process in enumerate(self.processes_data):
            pid = i + 1
            at = process["at"].value()
            bt = process["bt"].value()
            priority = process["priority"].value() if self.algorithm_choice == "Priority Scheduling" else 0
            self.processes.append((pid, at, bt, priority))
            process["remaining_bt"] = bt
            process["current_ct"] = 0
            process["completed"] = False
            process["ct"].setText("0")
            process["tat"].setText("0")
            process["waiting_time"].setText("0")
            print(f"Process P{pid}: AT={at}, BT={bt}, Priority={priority}")

    def update_timeline_and_gantt(self):
        """Update the timeline and Gantt chart after scheduling."""
        self.all_processes = sorted(set(pid for pid, _, _ in self.timeline))
        for pid, start, end in self.timeline:
            self.processes_data[pid - 1]["slices"].append((start, end))

        self.current_time = 0
        self.max_time = max(end for _, _, end in self.timeline) if self.timeline else 0
        self.current_timeline = []

        self.gantt_widget.processes = self.all_processes
        self.gantt_widget.timeline = self.current_timeline
        self.gantt_widget.max_time = self.max_time
        self.gantt_widget.update()

    def compileSimulation(self):
        """Compile and start the simulation for the selected algorithm."""
        self.initialize_processes()
        scheduler = self.get_scheduler()
        self.timeline = scheduler.calculate_completion_time()
        self.update_timeline_and_gantt()
        self.timer.start(100)

    def check_simulation_completion(self):
        """Check if the simulation has completed and finalize if so."""
        if self.current_time >= self.max_time:
            self.timer.stop()
            self.calculate_averages()
            self.cpu_label.setText(" Idle ")
            self.ready_queue_display.setText("Empty")
            QMessageBox.information(self, "Compile", "Simulation completed!")
            return True
        return False

    def find_current_process(self):
        """Find the process currently executing at the current time."""
        for pid, start, end in self.timeline:
            if start <= self.current_time < end:
                return pid
        return None

    def can_add_to_ready_queue(self, process, pid, current_pid, current_time):
        """Determine if a process should be added to the ready queue."""
        at = process["at"].value()
        bt = process["bt"].value()
        executed_time = sum(end - start for start, end in process["slices"] if end <= current_time + 1)
        remaining_time = bt - executed_time
        return (at <= current_time and not process["completed"] and 
                pid != current_pid and remaining_time > 0)

    def update_ready_queue(self, current_pid):
        """Update the ready queue based on current time and process status."""
        ready_queue = []
        for i, process in enumerate(self.processes_data):
            pid = i + 1
            if self.can_add_to_ready_queue(process, pid, current_pid, self.current_time):
                ready_queue.append((pid, process["at"].value()))

        ready_queue.sort(key=lambda x: x[1])
        display_text = " ".join(f"P{pid}" for pid, _ in ready_queue) if ready_queue else "Empty"
        self.ready_queue_display.setText(display_text)

    def calculate_executed_time(self, process):
        """Calculate the executed time for a process up to the current time."""
        return sum(end - start for start, end in process["slices"] if end <= self.current_time + 1)

    def update_process_on_completion(self, process, pid, total_bt):
        """Handle process completion, updating CT, TAT, and WT."""
        process["completed"] = True
        final_ct = max(end for _, end in process["slices"])
        process["ct"].setText(str(final_ct))
        tat = calculate_turnaround_time(process["at"].value(), final_ct)
        wt = calculate_waiting_time(tat, total_bt)
        process["tat"].setText(str(tat))
        process["waiting_time"].setText(str(wt))
        print(f"P{pid} completed at time {self.current_time}: CT={final_ct}, TAT={tat}, WT={wt}")

    def update_process_status(self):
        """Update the status bar, CT, TAT, and WT for each process."""
        for i, process in enumerate(self.processes_data):
            if process["completed"]:
                continue

            total_bt = process["bt"].value()
            executed_time = self.calculate_executed_time(process)
            progress = (executed_time / total_bt) * 100 if total_bt > 0 else 0
            process["status_bar"].setValue(min(int(progress), 100))
            process["current_ct"] = executed_time

            if executed_time > 0:
                current_ct = max(end for start, end in process["slices"] if end <= self.current_time + 1)
                process["ct"].setText(str(current_ct))

            if executed_time >= total_bt:
                self.update_process_on_completion(process, i + 1, total_bt)

    def update_gantt_chart(self):
        """Update the Gantt chart based on the current timeline."""
        self.current_timeline = [(pid, start, end) for pid, start, end in self.timeline if start <= self.current_time + 1]
        self.gantt_widget.timeline = self.current_timeline
        self.gantt_widget.max_time = self.max_time
        self.gantt_widget.update()

    def update_execution(self):
        """Update the simulation state for the current time step."""
        if self.check_simulation_completion():
            return

        current_pid = self.find_current_process()
        if current_pid is not None:
            self.cpu_label.setText(f" P{current_pid} ")
        else:
            self.cpu_label.setText(" Idle ")

        self.update_ready_queue(current_pid)
        self.update_process_status()
        self.update_gantt_chart()

        self.current_time += 1

    def calculate_averages(self):
        total_wt = 0
        total_tat = 0
        max_ct = 0
        for i, process in enumerate(self.processes_data):
            pid = i + 1
            if not process["completed"]:
                print(f"Warning: P{pid} did not complete!")
                continue

            final_ct = int(process["ct"].text())
            total_wt += int(process["waiting_time"].text())
            total_tat += int(process["tat"].text())
            max_ct = max(max_ct, final_ct)

        avg_wt = total_wt / self.process_quantity if self.process_quantity > 0 else 0
        avg_tat = total_tat / self.process_quantity if self.process_quantity > 0 else 0
        self.avgWtTime.setText(f"{avg_wt:.2f}")
        self.avgTaTime.setText(f"{avg_tat:.2f}")
        self.totalExecTime.setText(str(max_ct))

class CPUScheduler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setup_window_and_layout()
        self.setup_title()
        self.setup_algorithm_selection()
        self.setup_quantity_input()
        self.setup_buttons()

    def setup_window_and_layout(self):
        self.setWindowTitle("CPU Scheduling Simulation")
        self.setGeometry(100, 100, 900, 600)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setStyleSheet("""
            background-image: url('src/cpu-scheduling.jpg');
            background-repeat: no-repeat;
            background-position: center;
        """)
        self.layout = QVBoxLayout(self.centralWidget)
        self.top_layout = QVBoxLayout()

    def setup_title(self):
        self.label1 = QLabel("CPU Scheduling")
        font1 = QFont()
        font1.setPointSize(25)
        font1.setBold(True)
        self.label1.setFont(font1)
        self.label1.setAlignment(Qt.AlignHCenter)
        self.label1.setStyleSheet("color: white;background: transparent;")
        self.top_layout.addWidget(self.label1)

        self.label2 = QLabel("Simulation")
        font2 = QFont()
        font2.setPointSize(15)
        font2.setItalic(True)
        font2.setBold(True)
        self.label2.setFont(font2)
        self.label2.setAlignment(Qt.AlignHCenter)
        self.label2.setStyleSheet("color: white;background: transparent;")
        self.top_layout.addWidget(self.label2)

        self.top_layout.addSpacing(50)

    def setup_algorithm_selection(self):
        self.fixed_container = QWidget()
        self.fixed_container.setFixedWidth(350)
        self.fixed_container_layout = QVBoxLayout(self.fixed_container)

        self.choice_layout = QHBoxLayout()
        self.choiceLabel = self.create_label("Algorithm:", 15, 150)
        self.choice_layout.addWidget(self.choiceLabel)

        self.comboBox = self.create_combo_box(
            ["First Come First Serve (FCFS)", "Shortest Job First (SJF)", 
             "Priority Scheduling", "Round Robin (RR)"], 160, 40)
        self.comboBox.currentIndexChanged.connect(self.updateUI)
        self.choice_layout.addWidget(self.comboBox)

        self.fixed_container_layout.addLayout(self.choice_layout)
        self.fixed_container_layout.addSpacing(20)

    def setup_quantity_input(self):
        self.quantity_layout = QHBoxLayout()
        self.quantityLabel = self.create_label("Quantity:", 15, 140)
        self.quantity_layout.addWidget(self.quantityLabel)
        self.quantity_layout.addSpacing(10)

        self.quantitySpinBox = self.create_spin_box(1, 5, 1, 160, 35, font_size=10)
        self.quantity_layout.addWidget(self.quantitySpinBox)

        self.testcase_layout = QHBoxLayout()
        self.testcaseLabel = self.create_label("1 <= N <= 5", 10, 0)
        self.testcase_layout.addStretch()
        self.testcase_layout.addWidget(self.testcaseLabel)

        self.fixed_container_layout.addLayout(self.quantity_layout)
        self.fixed_container_layout.addLayout(self.testcase_layout)
        self.top_layout.addWidget(self.fixed_container, alignment=Qt.AlignHCenter)

        self.additional_layout = None
        self.time_quantum_layout = None
        self.extra_spacing = None
        self.newComboBox = None
        self.timeQuantumSpinBox = None

    def setup_buttons(self):
        self.bottom_layout = QHBoxLayout()
        self.start_btn = self.create_styled_button("Start", self.startSimulation)
        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.start_btn)
        self.bottom_layout.addStretch()

        self.exit_layout = QHBoxLayout()
        self.exit_btn = self.create_styled_button("Exit", self.exit_application)
        self.exit_layout.addStretch()
        self.exit_layout.addWidget(self.exit_btn)

        self.layout.addLayout(self.top_layout)
        self.layout.addSpacing(30)
        self.layout.addLayout(self.bottom_layout)
        self.layout.addStretch()
        self.layout.addLayout(self.exit_layout)

    def create_label(self, text, font_size, width):
        label = QLabel(text)
        font = QFont()
        font.setPointSize(font_size)
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("color: white; background: transparent;")
        if width:
            label.setFixedWidth(width)
        return label

    def create_combo_box(self, items, width, height):
        combo_box = QComboBox()
        combo_box.addItems(items)
        font = QFont("Arial", 10)
        combo_box.setFont(font)
        combo_box.setStyleSheet("color: black; background: white;")
        combo_box.setFixedSize(width, height)
        return combo_box

    def create_spin_box(self, min_val, max_val, default_val, width, height, font_size=10):
        spin_box = QSpinBox()
        spin_box.setFixedSize(width, height)
        spin_box.setRange(min_val, max_val)
        spin_box.setValue(default_val)
        spin_box.setStyleSheet("color: black;")
        font = QFont("Arial", font_size)
        spin_box.setFont(font)
        return spin_box

    def create_styled_button(self, text, slot):
        button = QPushButton(text)
        button.setFixedSize(100, 35)
        font = QFont("Arial", 10)
        font.setBold(True)
        button.setFont(font)
        button.setStyleSheet("color: black; background: white;")
        button.clicked.connect(slot)
        return button

    def exit_application(self):
        QApplication.quit()

    def updateUI(self):
        selected_text = self.comboBox.currentText()

        self.clear_layout(self.additional_layout)
        self.additional_layout = None
        self.newComboBox = None
        self.clear_layout(self.time_quantum_layout)
        self.time_quantum_layout = None
        self.timeQuantumSpinBox = None
        self.clear_layout(self.extra_spacing)
        self.extra_spacing = None

        if selected_text in ["Shortest Job First (SJF)", "Priority Scheduling"]:
            self.setup_sjf_priority_ui()
        elif selected_text == "Round Robin (RR)":
            self.setup_round_robin_ui()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.fixed_container_layout.removeItem(layout)

    def setup_sjf_priority_ui(self):
        self.extra_spacing = QVBoxLayout()
        self.extra_spacing.addSpacing(20)
        self.fixed_container_layout.addLayout(self.extra_spacing)

        self.additional_layout = QHBoxLayout()
        self.typeLabel = self.create_label("Type:", 15, 140)
        self.additional_layout.addWidget(self.typeLabel)

        self.newComboBox = self.create_combo_box(["Preemptive", "Non Preemptive"], 160, 35)
        self.additional_layout.addWidget(self.newComboBox)

        self.fixed_container_layout.addLayout(self.additional_layout)
        self.fixed_container_layout.setAlignment(Qt.AlignHCenter)

    def setup_round_robin_ui(self):
        self.extra_spacing = QVBoxLayout()
        self.extra_spacing.addSpacing(20)
        self.fixed_container_layout.addLayout(self.extra_spacing)

        self.time_quantum_layout = QHBoxLayout()
        self.timeQuantumLabel = self.create_label("Time Quantum:", 15, 200)
        self.time_quantum_layout.addWidget(self.timeQuantumLabel)
        self.time_quantum_layout.addSpacing(10)

        self.timeQuantumSpinBox = self.create_spin_box(1, 10, 2, 100, 35)
        self.time_quantum_layout.addWidget(self.timeQuantumSpinBox)

        self.fixed_container_layout.addLayout(self.time_quantum_layout)
        self.fixed_container_layout.setAlignment(Qt.AlignHCenter)

    def startSimulation(self):
        selected_algorithm = self.comboBox.currentText()
        process_quantity = self.quantitySpinBox.value()
        is_preemptive = self.newComboBox.currentText() == "Preemptive" if self.newComboBox else False
        time_quantum = self.timeQuantumSpinBox.value() if self.timeQuantumSpinBox else 2
        self.inner_window = InnerWindow(selected_algorithm, process_quantity, is_preemptive, time_quantum)
        self.inner_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CPUScheduler()
    window.show()
    sys.exit(app.exec_())