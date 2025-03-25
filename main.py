import os
import time
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
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

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
        self.setMinimumSize(600, 100)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(QFont("Arial", 10))
        width = self.width()
        height = self.height()
        row_height = height // max(1, len(self.processes))
        time_scale = width / max(1, self.max_time)

        painter.fillRect(self.rect(), QColor(255, 255, 255))  # White background

        colors = [QColor(255, 100, 100), QColor(100, 255, 100), QColor(100, 100, 255), QColor(255, 255, 100), QColor(255, 100, 255)]
        
        if self.timeline:
            for pid, start, end in self.timeline:
                row = self.processes.index(pid)
                y = row * row_height
                x_start = start * time_scale
                x_width = (end - start) * time_scale
                color = colors[row % len(colors)]
                painter.fillRect(int(x_start), y, int(x_width), row_height - 5, color)
                painter.drawText(int(x_start) + 5, y + row_height // 2, str(pid))

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
        self.setWindowTitle("Algorithm Execution")
        self.setGeometry(100, 100, 900, 700)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget) 
        
        self.centralWidget.setStyleSheet("""
            background-image: url('src/photo.jpeg');
            background-repeat: no-repeat;
            background-position: center;
        """)

        self.layout = QVBoxLayout(self.centralWidget)

        self.subMainLayout1 = QVBoxLayout()
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

        algo_text = f"{self.algorithm_choice}{' (Preemptive)' if self.is_preemptive else ' (Non-Preemptive)'}"
        self.algo_label = QLabel(algo_text)
        font = QFont()
        font.setPointSize(12)
        self.algo_label.setFont(font)
        self.algo_label.setAlignment(Qt.AlignLeft)
        self.algo_label.setStyleSheet("color: white; background: black;")
        self.algo_label.setAlignment(Qt.AlignCenter)
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
        self.subMainLayout1.addStretch()

        self.subMainLayout2 = QVBoxLayout()
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
            process_row = QHBoxLayout()

            priority_input = QSpinBox()
            priority_input.setRange(0, 100)
            priority_input.setValue(0)
            priority_input.setStyleSheet("color: black; background: white;")
            priority_input.setFixedWidth(90)
            priority_input.setFixedHeight(30)
            priority_input.setFont(QFont("Arial", 13))
            priority_input.setAlignment(Qt.AlignCenter)
            process_row.addWidget(priority_input)

            process_label = QLabel(f"P{i}")
            font = QFont("Arial", 13)
            process_label.setFont(font)
            process_label.setAlignment(Qt.AlignCenter)
            process_label.setStyleSheet("color: white; background: transparent;")
            process_label.setFixedWidth(110)
            process_row.addWidget(process_label)

            at_input = QSpinBox()
            at_input.setRange(0, 100)
            at_input.setValue(0)
            at_input.setStyleSheet("color: black; background: white;")
            at_input.setFixedWidth(90)
            at_input.setFixedHeight(30)
            at_input.setFont(QFont("Arial", 13))
            at_input.setAlignment(Qt.AlignCenter)
            process_row.addWidget(at_input)

            bt_input = QSpinBox()
            bt_input.setRange(1, 1000)
            bt_input.setValue(0)
            bt_input.setStyleSheet("color: black; background: white;")
            bt_input.setFixedWidth(90)
            bt_input.setFixedHeight(30)
            bt_input.setFont(QFont("Arial", 13))
            bt_input.setAlignment(Qt.AlignCenter)
            process_row.addWidget(bt_input)

            status_bar = QProgressBar()
            status_bar.setMaximum(100)
            status_bar.setValue(0)
            status_bar.setStyleSheet("QProgressBar { background-color: white; } QProgressBar::chunk { background-color: orange; }")
            status_bar.setFixedWidth(110)
            status_bar.setFixedHeight(30)
            status_bar.setAlignment(Qt.AlignCenter)
            process_row.addWidget(status_bar)

            ct_label = QLabel("0")
            font = QFont("Arial", 13)
            ct_label.setFont(font)
            ct_label.setAlignment(Qt.AlignCenter)
            ct_label.setStyleSheet("color: white; background: transparent;")
            ct_label.setFixedWidth(120)
            process_row.addWidget(ct_label)

            tat_label = QLabel("0")
            font = QFont("Arial", 13)
            tat_label.setFont(font)
            tat_label.setAlignment(Qt.AlignCenter)
            tat_label.setStyleSheet("color: white; background: transparent;")
            tat_label.setFixedWidth(120)
            process_row.addWidget(tat_label)

            waiting_time_label = QLabel("0")
            font = QFont("Arial", 13)
            waiting_time_label.setFont(font)
            waiting_time_label.setAlignment(Qt.AlignCenter)
            waiting_time_label.setStyleSheet("color: white; background: transparent;")
            waiting_time_label.setFixedWidth(120)
            process_row.addWidget(waiting_time_label)

            self.content.addLayout(process_row)
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
                "start_time": 0,
                "slices": [],
                "completed": False  # Track if the process has fully completed
            })

        self.processTableContent.addLayout(self.content)
        self.processTableLayout.addLayout(self.processTableContent)
        self.subMainLayout2.addLayout(self.processTableLayout)

        self.subMainLayout2_5 = QVBoxLayout()
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

        self.subMainLayout3 = QVBoxLayout()
        self.averageContainer = QWidget()
        self.averageContainer.setFixedHeight(135)
        self.averageContainer.setStyleSheet("background: transparent;")
        self.average_layout = QVBoxLayout(self.averageContainer)

        if self.algorithm_choice == "Round Robin (RR)":
            self.timeQuantum_layout = QHBoxLayout()
            self.timeQuantum_label = QLabel("Time Quantum: ")
            font = QFont()
            font.setPointSize(12)
            font.setBold(True)
            self.timeQuantum_label.setFont(font)
            self.timeQuantum_label.setAlignment(Qt.AlignLeft)
            self.timeQuantum_label.setStyleSheet("color: yellow; background: transparent;")
            self.timeQuantum_layout.addWidget(self.timeQuantum_label)

            self.timeQuantum_value = QLabel(str(self.time_quantum))
            font = QFont("Arial", 12)
            self.timeQuantum_value.setFont(font)
            self.timeQuantum_value.setAlignment(Qt.AlignLeft)
            self.timeQuantum_value.setStyleSheet("color: white; background: transparent;")
            self.timeQuantum_layout.addWidget(self.timeQuantum_value)
            self.timeQuantum_layout.addStretch()

            self.average_layout.addLayout(self.timeQuantum_layout)

        self.waitingTime_layout = QHBoxLayout()
        self.label = QLabel("Average Waiting Time: ")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setStyleSheet("color: yellow; background: transparent;")
        self.waitingTime_layout.addWidget(self.label)
        self.waitingTime_layout.addSpacing(40)

        self.avgWtTime = QLabel("0")
        font = QFont("Arial", 12)
        self.avgWtTime.setFont(font)
        self.avgWtTime.setAlignment(Qt.AlignLeft)
        self.avgWtTime.setStyleSheet("color: white; background: transparent;")
        self.waitingTime_layout.addWidget(self.avgWtTime)
        self.waitingTime_layout.addStretch()

        self.turnaroundTime_layout = QHBoxLayout()
        self.label = QLabel("Average Turnaround Time: ")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setStyleSheet("color: yellow; background: transparent;")
        self.turnaroundTime_layout.addWidget(self.label)

        self.avgTaTime = QLabel("0")
        font = QFont("Arial", 12)
        self.avgTaTime.setFont(font)
        self.avgTaTime.setAlignment(Qt.AlignLeft)
        self.avgTaTime.setStyleSheet("color: white; background: transparent;")
        self.turnaroundTime_layout.addWidget(self.avgTaTime)
        self.turnaroundTime_layout.addStretch()

        self.totalExecutionTime_layout = QHBoxLayout()
        self.label = QLabel("Total Execution Time: ")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setStyleSheet("color: yellow; background: transparent;")
        self.totalExecutionTime_layout.addWidget(self.label)
        self.totalExecutionTime_layout.addSpacing(55)

        self.totalExecTime = QLabel("0")
        font = QFont("Arial", 12)
        self.totalExecTime.setFont(font)
        self.totalExecTime.setAlignment(Qt.AlignLeft)
        self.totalExecTime.setStyleSheet("color: white; background: transparent;")
        self.totalExecutionTime_layout.addWidget(self.totalExecTime)
        self.totalExecutionTime_layout.addStretch()

        self.average_layout.addLayout(self.waitingTime_layout)
        self.average_layout.addLayout(self.turnaroundTime_layout)
        self.average_layout.addLayout(self.totalExecutionTime_layout)
        self.subMainLayout3.addWidget(self.averageContainer, alignment=Qt.AlignLeft)

        self.subMainLayout4 = QHBoxLayout()
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

        ready_queue_text = " ".join([f"P{i}" for i in range(2, self.process_quantity + 1)])
        self.ready_queue_display = QLabel(ready_queue_text if ready_queue_text else "Empty")
        font = QFont("Arial", 12)
        self.ready_queue_display.setFont(font)
        self.ready_queue_display.setAlignment(Qt.AlignLeft)
        self.ready_queue_display.setStyleSheet("color: white; background: black; padding: 5px;")
        self.readQueue_layout.addWidget(self.ready_queue_display)
        self.readQueue_layout.addStretch()

        self.subMainLayout4.addWidget(self.readyQueueContainer)
        self.subMainLayout4.addStretch()

        self.compile_btn = QPushButton("Compile")
        self.compile_btn.setFixedSize(100, 35)
        font = QFont("Arial", 10)
        font.setBold(True)
        self.compile_btn.setFont(font)
        self.compile_btn.setStyleSheet("color: black; background: white;")
        self.compile_btn.clicked.connect(self.compileSimulation)
        self.subMainLayout4.addWidget(self.compile_btn)

        self.layout.addLayout(self.subMainLayout1)
        self.layout.addLayout(self.subMainLayout2)
        self.layout.addLayout(self.subMainLayout2_5)
        self.layout.addStretch()
        self.layout.addLayout(self.subMainLayout3)
        self.layout.addLayout(self.subMainLayout4)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_execution)

    def compileSimulation(self):
        self.processes = []
        for i, process in enumerate(self.processes_data):
            pid = i + 1
            at = process["at"].value()
            bt = process["bt"].value()
            priority = process["priority"].value() if self.algorithm_choice == "Priority Scheduling" else 0
            self.processes.append((pid, at, bt, priority))
            process["remaining_bt"] = bt
            process["current_ct"] = 0
            process["start_time"] = 0
            process["completed"] = False
            # Initialize CT, TAT, WT labels
            process["ct"].setText("0")
            process["tat"].setText("0")
            process["waiting_time"].setText("0")
            print(f"Process P{pid}: AT={at}, BT={bt}, Priority={priority}")

        if self.algorithm_choice == "First Come First Serve (FCFS)":
            scheduler = FCFS([(pid, at, bt) for pid, at, bt, _ in self.processes])
        elif self.algorithm_choice == "Shortest Job First (SJF)":
            scheduler = SJF([(pid, at, bt) for pid, at, bt, _ in self.processes], self.is_preemptive)
        elif self.algorithm_choice == "Round Robin (RR)":
            scheduler = RoundRobin([(pid, at, bt) for pid, at, bt, _ in self.processes], self.time_quantum)
        elif self.algorithm_choice == "Priority Scheduling":
            scheduler = PriorityScheduling(self.processes, self.is_preemptive)

        self.timeline = scheduler.calculate_completion_time()
        print(f"Timeline: {self.timeline}")

        self.all_processes = sorted(set(pid for pid, _, _ in self.timeline))

        for pid, start, end in self.timeline:
            self.processes_data[pid - 1]["slices"].append((start, end))

        self.current_time = 0
        self.max_time = max(end for _, _, end in self.timeline) if self.timeline else 0
        self.current_timeline = []

        self.gantt_widget.processes = self.all_processes
        self.gantt_widget.timeline = self.current_timeline
        self.gantt_widget.max_time = self.current_time + 1
        self.gantt_widget.update()

        self.timer.start(100)

    def update_execution(self):
        if self.current_time > self.max_time:
            self.timer.stop()
            self.calculate_averages()
            self.cpu_label.setText(" Idle ")
            QMessageBox.information(self, "Compile", "Simulation completed!")
            return

        current_pid = None
        for pid, start, end in self.timeline:
            if start <= self.current_time < end:
                current_pid = pid
                break

        if current_pid is not None:
            self.cpu_label.setText(f" P{current_pid} ")
        else:
            self.cpu_label.setText(" Idle ")

        ready_queue = []
        for i, process in enumerate(self.processes_data):
            pid = i + 1
            at = process["at"].value()
            if at <= self.current_time and not process["completed"]:
                if pid != current_pid:
                    ready_queue.append(f"P{pid}")
        self.ready_queue_display.setText(" ".join(ready_queue) if ready_queue else "Empty")

        # Debug: Print CPU and Ready Queue state
        print(f"Time {self.current_time}: CPU={self.cpu_label.text().strip()}, Ready Queue={self.ready_queue_display.text()}")

        # Update Status Bar and CT dynamically
        for i, process in enumerate(self.processes_data):
            pid = i + 1
            if process["completed"]:
                continue  # Skip if process is already completed

            slices = process["slices"]
            total_bt = process["bt"].value()
            executed_time = 0

            for start, end in slices:
                if end <= self.current_time:
                    executed_time += end - start
                elif start <= self.current_time < end:
                    executed_time += self.current_time - start

            # Update current executed time
            process["current_ct"] = executed_time

            # Update Status Bar
            progress = (executed_time / total_bt) * 100 if total_bt > 0 else 0
            process["status_bar"].setValue(min(int(progress), 100))

            # Update CT dynamically (show current executed time)
            process["ct"].setText(str(int(executed_time)))

            # Check if process is completed
            if executed_time >= total_bt:
                process["completed"] = True
                # Set final CT as the end time of the last slice
                final_ct = max(end for _, end in process["slices"])
                process["ct"].setText(str(final_ct))
                print(f"P{pid} completed at time {self.current_time}, Final CT={final_ct}")

        self.current_timeline = [(pid, start, end) for pid, start, end in self.timeline if start <= self.current_time]
        self.gantt_widget.timeline = self.current_timeline
        self.gantt_widget.max_time = self.current_time + 1
        self.gantt_widget.update()

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

            # Final CT is already set in update_execution
            final_ct = int(process["ct"].text())
            at = process["at"].value()
            bt = process["bt"].value()
            tat = calculate_turnaround_time(at, final_ct)
            wt = calculate_waiting_time(tat, bt)

            # Update TAT and WT labels
            process["tat"].setText(str(tat))
            process["waiting_time"].setText(str(wt))

            total_wt += wt
            total_tat += tat
            max_ct = max(max_ct, final_ct)

            print(f"P{pid}: Final CT={final_ct}, TAT={tat}, WT={wt}")

        avg_wt = total_wt / self.process_quantity
        avg_tat = total_tat / self.process_quantity
        self.avgWtTime.setText(f"{avg_wt:.2f}")
        self.avgTaTime.setText(f"{avg_tat:.2f}")
        self.totalExecTime.setText(str(max_ct))

        self.gantt_widget.timeline = self.timeline
        self.gantt_widget.max_time = max_ct
        self.gantt_widget.update()

class CPUScheduler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("CPU Scheduling Simulation")
        self.setGeometry(100, 100, 900, 600)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)  
        
        self.layout = QVBoxLayout(self.centralWidget)

        self.top_layout = QVBoxLayout()

        self.centralWidget.setStyleSheet("""
            background-image: url('src/cpu-scheduling.jpg');
            background-repeat: no-repeat;
            background-position: center;
        """)

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

        self.fixed_container = QWidget()
        self.fixed_container.setFixedWidth(350)
        self.fixed_container_layout = QVBoxLayout(self.fixed_container)

        self.choice_layout = QHBoxLayout()
        self.choiceLabel = QLabel("Algorithm:")
        font3 = QFont()
        font3.setPointSize(15)
        font3.setBold(True)
        self.choiceLabel.setFont(font3)
        self.choiceLabel.setStyleSheet("color: white; background: transparent;")
        self.choiceLabel.setFixedWidth(150)
        self.choice_layout.addWidget(self.choiceLabel)

        self.comboBox = QComboBox()
        self.comboBox.addItems(["First Come First Serve (FCFS)", "Shortest Job First (SJF)", 
                              "Priority Scheduling", "Round Robin (RR)"])
        font = QFont("Arial", 10)
        self.comboBox.setFont(font)
        self.comboBox.setStyleSheet("color: black; background: white;")
        self.comboBox.setFixedSize(160, 40)
        self.comboBox.currentIndexChanged.connect(self.updateUI)
        self.choice_layout.addWidget(self.comboBox)

        self.quantity_layout = QHBoxLayout()
        self.quantityLabel = QLabel("Quantity:")
        font4 = QFont()
        font4.setPointSize(15)
        font4.setBold(True)
        self.quantityLabel.setFont(font4)
        self.quantityLabel.setStyleSheet("color: white; background: transparent;")
        self.quantityLabel.setFixedWidth(140)
        self.quantity_layout.addWidget(self.quantityLabel)
        self.quantity_layout.addSpacing(10)

        self.quantitySpinBox = QSpinBox()
        self.quantitySpinBox.setFixedSize(160, 35)
        self.quantitySpinBox.setRange(1, 5)
        self.quantitySpinBox.setStyleSheet("color: black;")
        font = QFont("Arial", 10)
        self.quantitySpinBox.setFont(font)
        self.quantity_layout.addWidget(self.quantitySpinBox)

        self.testcase_layout = QHBoxLayout()
        self.testcaseLabel = QLabel("1 <= N <= 5")
        font4 = QFont()
        font4.setPointSize(10)
        self.testcaseLabel.setFont(font4)
        self.testcaseLabel.setStyleSheet("color: white; background: transparent;")
        self.testcase_layout.addStretch()
        self.testcase_layout.addWidget(self.testcaseLabel)

        self.fixed_container_layout.addLayout(self.choice_layout)
        self.fixed_container_layout.addSpacing(20)
        self.fixed_container_layout.addLayout(self.quantity_layout)
        self.fixed_container_layout.addLayout(self.testcase_layout)

        self.top_layout.addWidget(self.fixed_container, alignment=Qt.AlignHCenter)

        self.additional_layout = None
        self.time_quantum_layout = None

        self.bottom_layout = QVBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.setFixedSize(150, 35)
        font = QFont("Arial", 10)
        font.setBold(True)
        self.start_btn.setFont(font)
        self.start_btn.setStyleSheet("color: black; background: white;")
        self.start_btn.clicked.connect(self.startSimulation)
        self.bottom_layout.addWidget(self.start_btn)
        self.bottom_layout.setAlignment(Qt.AlignHCenter)

        self.layout.addLayout(self.top_layout)
        self.layout.addSpacing(30)
        self.layout.addLayout(self.bottom_layout)
        self.layout.addStretch()

    def updateUI(self):
        selected_text = self.comboBox.currentText()

        if self.additional_layout:
            while self.additional_layout.count():
                item = self.additional_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.fixed_container_layout.removeItem(self.additional_layout)
            del self.additional_layout
            self.additional_layout = None

        if hasattr(self, 'time_quantum_layout') and self.time_quantum_layout:
            while self.time_quantum_layout.count():
                item = self.time_quantum_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.fixed_container_layout.removeItem(self.time_quantum_layout)
            del self.time_quantum_layout
            self.time_quantum_layout = None

        for i in range(self.fixed_container_layout.count()):
            item = self.fixed_container_layout.itemAt(i)
            if isinstance(item, QVBoxLayout):
                self.fixed_container_layout.removeItem(item)

        if selected_text in ["Shortest Job First (SJF)", "Priority Scheduling"]:
            self.extra_spacing = QVBoxLayout()
            self.extra_spacing.addSpacing(20)
            self.fixed_container_layout.addLayout(self.extra_spacing)

            self.additional_layout = QHBoxLayout()
            self.typeLabel = QLabel("Type:")
            font4 = QFont()
            font4.setPointSize(15)
            font4.setBold(True)
            self.typeLabel.setFont(font4)
            self.typeLabel.setStyleSheet("color: white; background: transparent;")
            self.typeLabel.setFixedWidth(140)
            self.additional_layout.addWidget(self.typeLabel)

            self.newComboBox = QComboBox()
            self.newComboBox.addItems(["Preemptive", "Non Preemptive"])
            font5 = QFont("Arial", 10)
            self.newComboBox.setFont(font5)
            self.newComboBox.setStyleSheet("color: black; background: white;")
            self.newComboBox.setFixedSize(160, 35)
            self.additional_layout.addWidget(self.newComboBox)

            self.fixed_container_layout.addLayout(self.additional_layout)
            self.fixed_container_layout.setAlignment(Qt.AlignHCenter)

        if selected_text == "Round Robin (RR)":
            self.extra_spacing = QVBoxLayout()
            self.extra_spacing.addSpacing(20)
            self.fixed_container_layout.addLayout(self.extra_spacing)

            self.time_quantum_layout = QHBoxLayout()
            self.timeQuantumLabel = QLabel("Time Quantum:")
            font4 = QFont()
            font4.setPointSize(15)
            font4.setBold(True)
            self.timeQuantumLabel.setFont(font4)
            self.timeQuantumLabel.setStyleSheet("color: white; background: transparent;")
            self.timeQuantumLabel.setFixedWidth(200)
            self.time_quantum_layout.addWidget(self.timeQuantumLabel)
            self.time_quantum_layout.addSpacing(10)

            self.timeQuantumSpinBox = QSpinBox()
            self.timeQuantumSpinBox.setFixedSize(100, 35)
            self.timeQuantumSpinBox.setRange(1, 10)
            self.timeQuantumSpinBox.setValue(2)
            self.timeQuantumSpinBox.setStyleSheet("color: black;")
            font = QFont("Arial", 10)
            self.timeQuantumSpinBox.setFont(font)
            self.time_quantum_layout.addWidget(self.timeQuantumSpinBox)

            self.fixed_container_layout.addLayout(self.time_quantum_layout)
            self.fixed_container_layout.setAlignment(Qt.AlignHCenter)

    def startSimulation(self):
        selected_algorithm = self.comboBox.currentText()
        process_quantity = self.quantitySpinBox.value()
        is_preemptive = self.newComboBox.currentText() == "Preemptive" if self.additional_layout else False
        time_quantum = self.timeQuantumSpinBox.value() if hasattr(self, 'timeQuantumSpinBox') else 2
        self.inner_window = InnerWindow(selected_algorithm, process_quantity, is_preemptive, time_quantum)
        self.inner_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CPUScheduler()
    window.show()
    sys.exit(app.exec_())