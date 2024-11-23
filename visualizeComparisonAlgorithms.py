import os
import timeit
import matplotlib.pyplot as plt
import numpy as np
from backwardChaining import BackwardChaining
from forwardChaining import ForwardChaining
from dpll import DPLL
from resolution import Resolution
from truthTable import TruthTable

# Initialize data structures
algorithms = ["Forward Chaining", "Backward Chaining"]
execution_times = {alg: [] for alg in algorithms}
files_processed = []

# Define the directory containing test files
test_directory = "test_case"

# Process each test file
txt_files = [f for f in os.listdir(test_directory) if f.endswith('.txt') and (f.startswith('test_Horn_Implication') or f.startswith('test_Horn_Mix')) and not (f.endswith('4.txt') or f.endswith('5.txt'))]

for file in txt_files:
    file_path = os.path.join(test_directory, file)

    # Measure Forward Chaining
    fc_time = timeit.timeit(lambda: ForwardChaining(file_path).infer(), number=1)
    execution_times["Forward Chaining"].append(fc_time)

    # Measure Backward Chaining
    bc_time = timeit.timeit(lambda: BackwardChaining(file_path).infer(), number=1)
    execution_times["Backward Chaining"].append(bc_time)

    files_processed.append(file)

# Visualization
bar_width = 0.35
index = np.arange(len(files_processed))

# Plot Execution Times
plt.figure(figsize=(12, 6))
plt.bar(index, execution_times["Forward Chaining"], bar_width, label="Forward Chaining")
plt.bar(index + bar_width, execution_times["Backward Chaining"], bar_width, label="Backward Chaining")

plt.xlabel('Test Files')
plt.ylabel('Execution Time (seconds)')
plt.title('Execution Time: Forward vs Backward Chaining')
plt.xticks(index + bar_width / 2, files_processed, rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

# Initialize data structures
algorithms = ["DPLL", "Resolution", "Truth Table"]
execution_times = {alg: [] for alg in algorithms}
files_processed = []

# Define the directory containing test files
test_directory = "test_case"  # Update with your test cases directory

# Filter test files
txt_files = [f for f in os.listdir(test_directory) if f.endswith('.txt') and f.startswith('test_Generic') and f not in ['test_Generic_5.txt', 'test_Generic_6.txt', 'test_Generic_7.txt', 'test_Generic_10.txt']]

for file in txt_files:
    file_path = os.path.join(test_directory, file)

    # Measure execution time for DPLL
    dpll_time = timeit.timeit(lambda: DPLL(file_path).infer(), number=1)
    execution_times["DPLL"].append(dpll_time)

    # Measure execution time for Resolution
    resolution_time = timeit.timeit(lambda: Resolution(file_path).infer(), number=1)
    execution_times["Resolution"].append(resolution_time)

    # Measure execution time for Truth Table
    truth_table_time = timeit.timeit(lambda: TruthTable(file_path).infer(), number=1)
    execution_times["Truth Table"].append(truth_table_time)

    files_processed.append(file)

# Visualization
bar_width = 0.25
index = np.arange(len(files_processed))

# Plot Execution Times
plt.figure(figsize=(14, 7))
for i, algorithm in enumerate(algorithms):
    plt.bar(index + i * bar_width, execution_times[algorithm], bar_width, label=algorithm)

plt.xlabel('Test Files')
plt.ylabel('Execution Time (seconds)')
plt.title('Execution Time Comparison: DPLL, Resolution, Truth Table')
plt.xticks(index + bar_width, files_processed, rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

# Initialize data structures
algorithms = ["DPLL", "Truth Table"]
execution_times = {alg: [] for alg in algorithms}
files_processed = []

# Define the directory containing test files
test_directory = "test_case"  # Update this to the path of your test case directory

# Filter test files
txt_files = ['test_Generic_5.txt', 'test_Generic_6.txt', 'test_Generic_7.txt', 'test_Generic_10.txt']

for file in txt_files:
    file_path = os.path.join(test_directory, file)

    # Measure execution time for DPLL
    dpll_time = timeit.timeit(lambda: DPLL(file_path).infer(), number=1)
    execution_times["DPLL"].append(dpll_time)

    # Measure execution time for Truth Table
    tt_time = timeit.timeit(lambda: TruthTable(file_path).infer(), number=1)
    execution_times["Truth Table"].append(tt_time)

    files_processed.append(file)

# Visualization
bar_width = 0.35
index = np.arange(len(files_processed))

# Plot Execution Times
plt.figure(figsize=(14, 7))
for i, algorithm in enumerate(algorithms):
    plt.bar(index + i * bar_width, execution_times[algorithm], bar_width, label=algorithm)

plt.xlabel('Test Files')
plt.ylabel('Execution Time (seconds)')
plt.title('Execution Time Comparison: DPLL vs Truth Table')
plt.xticks(index + bar_width / 2, files_processed, rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

