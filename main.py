import os
import time
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, 
                            QMainWindow, QHBoxLayout, QSpinBox, QPushButton, 
                            QMessageBox, QTextEdit, QProgressBar)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

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

class InnerWindow(QMainWindow):
    def __init__(self, algorithm_choice, process_quantity, is_preemptive):
        super().__init__()
        self.algorithm_choice = algorithm_choice
        self.process_quantity = process_quantity
        self.is_preemptive = is_preemptive
        self.processes = []
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Algorithm Execution")
        self.setGeometry(100, 100, 900, 600)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget) 
        
        self.centralWidget.setStyleSheet("""
            background-image: url('src/photo.jpeg');
            background-repeat: no-repeat;
            background-position: center;
        """)

        self.layout = QVBoxLayout(self.centralWidget)

        # SubMainLayout1: Algorithm and CPU Display
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

        self.cpu_label = QLabel(" P1 ")
        font = QFont()
        font.setPointSize(12)
        self.cpu_label.setFont(font)
        self.cpu_label.setAlignment(Qt.AlignLeft)
        self.cpu_label.setStyleSheet("color: white; background: black;")
        self.cpu_label.setAlignment(Qt.AlignCenter)
        self.cpu_Layout.addWidget(self.cpu_label)
        self.cpu_Layout.addStretch()

        self.top_Layout.addLayout(self.algo_Layout)
        self.top_Layout.addLayout(self.cpu_Layout)
        self.top_Layout.addStretch()

        self.subMainLayout1.addLayout(self.top_Layout)
        self.subMainLayout1.addStretch()

        # SubMainLayout2: Process Table (Made Responsive)
        self.subMainLayout2 = QVBoxLayout()
        self.processTableLayout = QHBoxLayout()
        self.processTableContent = QVBoxLayout()

        self.heading = QVBoxLayout()
        self.column = QHBoxLayout()

        # Header with fixed widths
        headers = ["Priority", "Processes", "AT", "BT", "Status Bar", "CT", "TAT", "WT"]
        for title in headers:
            label = QLabel(title)
            font = QFont()
            font.setPointSize(12)
            font.setBold(True)
            label.setFont(font)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: yellow; background: transparent;")
            label.setFixedWidth(80 if title in ["Priority", "AT", "BT"] else 100)  # Adjusted widths
            self.column.addWidget(label)

        self.heading.addLayout(self.column)
        self.processTableContent.addLayout(self.heading)

        self.content = QVBoxLayout()
        self.processes_data = []

        for i in range(1, self.process_quantity + 1):
            process_row = QHBoxLayout()

            # Priority
            priority_input = QSpinBox()
            priority_input.setRange(0, 100)
            priority_input.setValue(0)
            priority_input.setStyleSheet("color: black; background: white;")
            priority_input.setFixedWidth(80)
            priority_input.setAlignment(Qt.AlignCenter)
            process_row.addWidget(priority_input)

            # Process
            process_label = QLabel(f"P{i}")
            font = QFont("Arial", 12)
            process_label.setFont(font)
            process_label.setAlignment(Qt.AlignCenter)
            process_label.setStyleSheet("color: white; background: transparent;")
            process_label.setFixedWidth(100)
            process_row.addWidget(process_label)

            # AT
            at_input = QSpinBox()
            at_input.setRange(0, 100)
            at_input.setValue(0)
            at_input.setStyleSheet("color: black; background: white;")
            at_input.setFixedWidth(80)
            at_input.setAlignment(Qt.AlignCenter)
            process_row.addWidget(at_input)

            # BT
            bt_input = QSpinBox()
            bt_input.setRange(1, 1000)
            bt_input.setValue(0)
            bt_input.setStyleSheet("color: black; background: white;")
            bt_input.setFixedWidth(80)
            bt_input.setAlignment(Qt.AlignCenter)
            process_row.addWidget(bt_input)

            # Status Bar
            status_bar = QProgressBar()
            status_bar.setMaximum(100)
            status_bar.setValue(0)
            status_bar.setStyleSheet("QProgressBar { background-color: white; } QProgressBar::chunk { background-color: orange; }")
            status_bar.setFixedWidth(100)
            status_bar.setAlignment(Qt.AlignCenter)
            process_row.addWidget(status_bar)

            # CT
            ct_label = QLabel("0")
            font = QFont("Arial", 12)
            ct_label.setFont(font)
            ct_label.setAlignment(Qt.AlignCenter)
            ct_label.setStyleSheet("color: white; background: transparent;")
            ct_label.setFixedWidth(100)  # Fixed width for multi-digit stability
            process_row.addWidget(ct_label)

            # TAT
            tat_label = QLabel("0")
            font = QFont("Arial", 12)
            tat_label.setFont(font)
            tat_label.setAlignment(Qt.AlignCenter)
            tat_label.setStyleSheet("color: white; background: transparent;")
            tat_label.setFixedWidth(100)  # Fixed width for multi-digit stability
            process_row.addWidget(tat_label)

            # WT
            waiting_time_label = QLabel("0")
            font = QFont("Arial", 12)
            waiting_time_label.setFont(font)
            waiting_time_label.setAlignment(Qt.AlignCenter)
            waiting_time_label.setStyleSheet("color: white; background: transparent;")
            waiting_time_label.setFixedWidth(100)  # Fixed width for multi-digit stability
            process_row.addWidget(waiting_time_label)

            self.content.addLayout(process_row)
            self.processes_data.append({
                "priority": priority_input,
                "at": at_input,
                "bt": bt_input,
                "status_bar": status_bar,
                "ct": ct_label,
                "tat": tat_label,
                "waiting_time": waiting_time_label
            })

        self.processTableContent.addLayout(self.content)
        self.processTableLayout.addLayout(self.processTableContent)
        self.subMainLayout2.addLayout(self.processTableLayout)

        # SubMainLayout3: Average Times
        self.subMainLayout3 = QVBoxLayout()
        self.averageContainer = QWidget()
        self.averageContainer.setFixedHeight(100)
        self.averageContainer.setStyleSheet("background: transparent;")
        self.average_layout = QVBoxLayout(self.averageContainer)

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

        # SubMainLayout4: Ready Queue and Compile Button
        self.subMainLayout4 = QHBoxLayout()
        self.readyQueueContainer = QWidget()
        self.readyQueueContainer.setFixedHeight(60)
        self.readyQueueContainer.setStyleSheet("background: transparent;")
        self.readQueue_layout = QHBoxLayout(self.readyQueueContainer)

        self.label = QLabel("Ready Queuee ")
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
        self.layout.addStretch()
        self.layout.addLayout(self.subMainLayout3)
        self.layout.addLayout(self.subMainLayout4)

    def compileSimulation(self):
        self.processes = []
        for i, process in enumerate(self.processes_data):
            pid = i + 1
            at = process["at"].value()
            bt = process["bt"].value()
            priority = process["priority"].value() if self.algorithm_choice == "Priority Scheduling" else 0
            self.processes.append((pid, at, bt, priority))

        if self.algorithm_choice == "First Come First Serve (FCFS)":
            scheduler = FCFS([(pid, at, bt) for pid, at, bt, _ in self.processes])
        elif self.algorithm_choice == "Shortest Job First (SJF)":
            scheduler = SJF([(pid, at, bt) for pid, at, bt, _ in self.processes], self.is_preemptive)
        elif self.algorithm_choice == "Round Robin (RR)":
            time_quantum = 2
            scheduler = RoundRobin([(pid, at, bt) for pid, at, bt, _ in self.processes], time_quantum)
        elif self.algorithm_choice == "Priority Scheduling":
            scheduler = PriorityScheduling(self.processes, self.is_preemptive)

        schedule = scheduler.calculate_completion_time()
        completion_times = {pid: ctime for pid, ctime in schedule}

        total_wt = 0
        total_tat = 0
        max_ct = 0
        for i, (pid, at, bt, _) in enumerate(self.processes):
            ct = completion_times[pid]
            tat = calculate_turnaround_time(at, ct)
            wt = calculate_waiting_time(tat, bt)
            
            self.processes_data[i]["ct"].setText(str(ct))
            self.processes_data[i]["tat"].setText(str(tat))
            self.processes_data[i]["waiting_time"].setText(str(wt))
            
            total_wt += wt
            total_tat += tat
            max_ct = max(max_ct, ct)

        avg_wt = total_wt / self.process_quantity
        avg_tat = total_tat / self.process_quantity
        self.avgWtTime.setText(f"{avg_wt:.2f}")
        self.avgTaTime.setText(f"{avg_tat:.2f}")
        self.totalExecTime.setText(str(max_ct))

        QMessageBox.information(self, "Compile", "Simulation completed!")

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

    def startSimulation(self):
        selected_algorithm = self.comboBox.currentText()
        process_quantity = self.quantitySpinBox.value()
        is_preemptive = self.newComboBox.currentText() == "Preemptive" if self.additional_layout else False
        self.inner_window = InnerWindow(selected_algorithm, process_quantity, is_preemptive)
        self.inner_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CPUScheduler()
    window.show()
    sys.exit(app.exec_())