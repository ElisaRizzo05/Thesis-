import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.ticker import ScalarFormatter

# def create_graphs_no_tukey(hash_mode, GPUs_speeds, CPUs_speeds):
#     # Extract speed values for GPUs and CPUs
#     GPU_speeds = [speed[3] for speed in GPUs_speeds]
#     CPU_speeds = [speed[3] for speed in CPUs_speeds]

#     # Create a box plot
#     plt.figure(figsize=(8, 6))
#     plt.boxplot([GPU_speeds, CPU_speeds], labels=['GPUs', 'CPUs'])
#     plt.title(f'Speed Distribution for Hash Mode: {hash_mode}')
#     plt.ylabel('Speed')
#     plt.xlabel('Device Type')

#     # Save the plot in the 'plots' folder
#     plt.savefig(os.path.join(os.path.dirname(__file__), "plots", "general_by_hash_no_tukey", f'boxplot_{hash_mode}.png'))

#     # Show the plot
#     plt.show()

def tukey_method(data):
    if data != 0:
        # Calculate the first quartile (Q1) and third quartile (Q3)
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)

        # Calculate the IQR (Interquartile Range)
        IQR = Q3 - Q1

        # Define the lower and upper bounds for outliers 1.5 di solito
        lower_bound = Q1 - 4.0 * IQR
        upper_bound = Q3 + 4.0 * IQR

        # Filter out values outside the bounds (outliers)
        filtered_data = [x for x in data if lower_bound <= x <= upper_bound]

        return filtered_data

def create_graphs(hash_mode, GPUs_speeds, CPUs_speeds):
    # Extract speed values for GPUs and CPUs
    GPU_speeds = [speed[3] for speed in GPUs_speeds]
    CPU_speeds = [speed[3] for speed in CPUs_speeds]

    # Apply the Tukey method to remove outliers and keep original data for median calculation
    filtered_GPU_speeds = tukey_method(GPU_speeds)
    filtered_CPU_speeds = tukey_method(CPU_speeds)

    # Create a box plot
    plt.figure(figsize=(8, 6))
    plt.boxplot([filtered_GPU_speeds, filtered_CPU_speeds], labels=['GPUs', 'CPUs'])
    plt.title(f'Speed Distribution for Hash Mode: {hash_mode}')
    plt.yscale('log')
    plt.ylabel('Speed')
    plt.xlabel('Device Type')

    # Save the plot in the 'plots' folder
    plt.savefig(os.path.join(os.path.dirname(__file__), "plots", "general_by_hash_tukey", f'boxplot_{hash_mode}.png'))

    # Show the plot
    plt.show()

def create_gpu_boxplot(hash_mode, GPUs_speeds):
    # Extract speed values for GPUs
    GPU_speeds = [speed[3] for speed in GPUs_speeds]

    # Apply the Tukey method to remove outliers and keep original data for median calculation
    filtered_GPU_speeds = tukey_method(GPU_speeds)

    # Create a box plot for GPUs
    plt.figure(figsize=(6, 6))
    plt.boxplot([filtered_GPU_speeds], labels=['GPUs'])
    plt.title(f'Speed Distribution for Hash Mode: {hash_mode}')
    plt.ylabel('Speed')
    plt.xlabel('Device Type')

    # Save the plot in the 'plots' folder
    plt.savefig(os.path.join(os.path.dirname(__file__), "plots", "general_by_hash_tukey", f'gpu_boxplot_{hash_mode}.png'))

    # Show the plot
    plt.show()

def create_cpu_boxplot(hash_mode, CPUs_speeds):
    # Extract speed values for CPUs
    CPU_speeds = [speed[3] for speed in CPUs_speeds]

    # Apply the Tukey method to remove outliers and keep original data for median calculation
    filtered_CPU_speeds = tukey_method(CPU_speeds)

    # Create a box plot for CPUs
    plt.figure(figsize=(6, 6))
    plt.boxplot([filtered_CPU_speeds], labels=['CPUs'])
    plt.title(f'Speed Distribution for Hash Mode: {hash_mode}')
    plt.ylabel('Speed')
    plt.xlabel('Device Type')

    # Save the plot in the 'plots' folder
    plt.savefig(os.path.join(os.path.dirname(__file__), "plots", "general_by_hash_tukey", f'cpu_boxplot_{hash_mode}.png'))

    # Show the plot
    plt.show()

def create_all_graphs(hash_mode, GPUs_speeds, CPUs_speeds):
    # create_graphs_no_tukey(hash_mode, GPUs_speeds, CPUs_speeds)
    create_graphs(hash_mode, GPUs_speeds, CPUs_speeds)
    # create_gpu_boxplot(hash_mode, GPUs_speeds)
    # create_cpu_boxplot(hash_mode, CPUs_speeds)

def calculate_slope(x_values, y_values):
    # Calculate the angular coefficient (slope) of a line using linear regression
    n = len(x_values)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x_squared = sum(x ** 2 for x in x_values)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x ** 2)
    
    return slope

def create_iteration_graph(hash_mode, iterations, GPU, CPU):
    # Extract relevant data for CPU and GPU
    cpu_data = CPU[hash_mode]
    gpu_data = GPU[hash_mode]
    
    # Initialize lists to store data for plotting
    x_values = list(range(iterations[hash_mode][0], iterations[hash_mode][1] + 1))
    cpu_y_values = []
    gpu_y_values = []
    
    # Calculate and append y-values for CPU and GPU
    for it in x_values:
        cpu_y = (iterations[hash_mode][2] / cpu_data[0][1]) * it
        gpu_y = (iterations[hash_mode][2] / gpu_data[0][1]) * it
        cpu_y_values.append(cpu_y)
        gpu_y_values.append(gpu_y)
    
    # Calculate the slopes of the CPU and GPU lines
    cpu_slope = calculate_slope(x_values, cpu_y_values)
    gpu_slope = calculate_slope(x_values, gpu_y_values)
    
    # Print the slopes
    print(f"Slope of CPU line for {hash_mode}: {cpu_slope}")
    print(f"Slope of GPU line for {hash_mode}: {gpu_slope}")

    # Create the graph
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, cpu_y_values, label=cpu_data[0][0], color='green')
    plt.plot(x_values, gpu_y_values, label=gpu_data[0][0], color='blue')
    
    # Set graph title and labels
    plt.title(f"{hash_mode} Iteration Comparison")
    plt.xlabel("Number of Iterations")
    plt.ylabel("Time (s)")
    plt.yscale("log")
    
    # Disable scientific notation for x-axis
    plt.ticklabel_format(style='plain', axis='x')

    # plt.ticklabel_format(style='plain')
    # plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=False))

    # Show legend
    plt.legend()
    
    # Show the graph
    plt.grid(True)

    # Save the plot in the 'plots' folder
    plt.savefig(os.path.join(os.path.dirname(__file__), "plots", "attacker_client_comparison", f'{hash_mode}_comparison.png'))

    plt.show()

def create_medium_iteration_graphs(hash_mode, iterations, GPU, CPU):
    # Extract relevant data for CPU and GPU
    cpu_data = CPU[hash_mode]
    gpu_data = GPU[hash_mode]
    
    # Initialize lists to store data for plotting
    x_values = list(range(iterations[hash_mode][0], iterations[hash_mode][1] + 1))
    cpu_y_values = []
    gpu_y_values = []
    
    # Calculate and append y-values for CPU and GPU
    for it in x_values:
        cpu_y = (iterations[hash_mode][2] / cpu_data[0][1]) * it
        gpu_y = (iterations[hash_mode][2] / gpu_data[0][1]) * it
        cpu_y_values.append(cpu_y)
        gpu_y_values.append(gpu_y)
    
    # Calculate the slopes of the CPU and GPU lines
    cpu_slope = calculate_slope(x_values, cpu_y_values)
    gpu_slope = calculate_slope(x_values, gpu_y_values)
    
    # Print the slopes
    print(f"Slope of CPU line for {hash_mode}: {cpu_slope}")
    print(f"Slope of GPU line for {hash_mode}: {gpu_slope}")

    # Create the graph
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, cpu_y_values, label=cpu_data[0][0], color='green')
    plt.plot(x_values, gpu_y_values, label=gpu_data[0][0], color='blue')
    
    # Set graph title and labels
    plt.title(f"{hash_mode} Iteration Comparison")
    plt.xlabel("Number of Iterations")
    plt.ylabel("Time (s)")
    plt.yscale("log")
    
    # Disable scientific notation for x-axis
    plt.ticklabel_format(style='plain', axis='x')

    # plt.ticklabel_format(style='plain')
    # plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=False))

    # Show legend
    plt.legend()
    
    # Show the graph
    plt.grid(True)

    # Save the plot in the 'plots' folder
    plt.savefig(os.path.join(os.path.dirname(__file__), "plots", "medium_attacker_client_comparison", f'{hash_mode}_comparison.png'))

    plt.show()


def create_cpu_iteration_graphs(hash_mode, iterations, CPU):
    cpu_data = CPU[hash_mode]

    print("cpu_data[0][1] ", cpu_data[0][1])

    # Initialize lists to store data for plotting
    x_values = list(range(iterations[hash_mode][0], iterations[hash_mode][1] + 1))
    cpu_y_values = []
    
    # Calculate and append y-values for CPU and GPU
    for it in x_values:
        cpu_y = (iterations[hash_mode][2] / cpu_data[0][1]) * it
        cpu_y_values.append(cpu_y)
    
    # Calculate the slopes of the CPU and GPU lines
    cpu_slope = calculate_slope(x_values, cpu_y_values)
    
    # Print the slopes
    print(f"Slope of CPU line for {hash_mode}: {cpu_slope}")

    # Create the graph
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, cpu_y_values, label=cpu_data[0][0], color='green')
    
    # Set graph title and labels
    plt.title(f"{hash_mode} Iteration Comparison")
    plt.xlabel("Number of Iterations")
    plt.ylabel("Time (s)")
    plt.yscale("log")
    
    # Disable scientific notation for x-axis
    plt.ticklabel_format(style='plain', axis='x')

    # Show legend
    plt.legend()
    
    # Show the graph
    plt.grid(True)

    # Save the plot in the 'plots' folder
    plt.savefig(os.path.join(os.path.dirname(__file__), "plots", "medium_attacker_client_comparison", f'{hash_mode}_comparison.png'))

    plt.show()

    
def create_gpu_iteration_graphs(hash_mode, iterations, GPU):
    gpu_data = GPU[hash_mode]

    print("gpu_data ", hash_mode,"    ", gpu_data)


def create_all_iteration_graphs(hash_mode, iterations, GPU, CPU):
    create_iteration_graph(hash_mode, iterations, GPU, CPU)
    create_medium_iteration_graphs(hash_mode, iterations, GPU, CPU)
    
def create_cpu_gpu_iteration_graphs(hash_mode, iterations, GPU, CPU):
    create_cpu_iteration_graphs(hash_mode, iterations, CPU)
    create_gpu_iteration_graphs(hash_mode, iterations, GPU)