# CPU Scheduling Simulation

A PyQt5-based application to simulate CPU scheduling algorithms, including First Come First Serve (FCFS), Shortest Job First (SJF), Round Robin (RR), and Priority Scheduling.

## Features

- Supports both preemptive and non-preemptive scheduling modes for SJF and Priority Scheduling.
- Visualizes the scheduling process with a real-time Gantt chart.
- Displays CPU and Ready Queue states during execution.
- Calculates and displays Completion Time (CT), Turnaround Time (TAT), and Waiting Time (WT) for each process.
- Provides average TAT and WT for the entire simulation.

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Setup

1. Create a virtual environment:

```bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
   pip install -r requirements.txt
```

3. Run the application:

```bash
   python main.py
```

## Usage

1. Launch the application using the setup instructions above.
2. In the main window, select a scheduling algorithm (FCFS, SJF, Priority Scheduling, or Round Robin) from the dropdown menu.
3. Specify the number of processes (1 to 5) using the quantity spin box.
4. For SJF or Priority Scheduling, choose between preemptive or non-preemptive mode using the "Type" dropdown.
5. For Round Robin, set the time quantum using the spin box (default is 2).
6. Click "Start" to open the simulation window.
7. In the simulation window, enter the Arrival Time (AT), Burst Time (BT), and Priority (if applicable) for each process using the input fields.
8. Click "Compile" to run the simulation. The Gantt chart, CPU/Ready Queue states, and process metrics (CT, TAT, WT) will update in real-time.
9. View the average TAT, average WT, and total execution time at the bottom of the simulation window.

## Project Structure

- `main.py`: Main application file
- `fcfs.py`, `sjf.py`, `roundRobin.py`, `priorityScheduling.py`: Scheduling algorithm implementations
- `src/`: Directory containing background images (`photo.jpeg`, `cpu-scheduling.jpg`)
