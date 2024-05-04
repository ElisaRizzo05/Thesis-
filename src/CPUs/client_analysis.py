import matplotlib.pyplot as plt
import os
import numpy as np
import database
from sklearn.cluster import KMeans


def tukey_method(data):
    if len(data) == 0:
        return []

    # Calculate the first quartile (Q1) and third quartile (Q3)
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)

    # Calculate the interquartile range (IQR)
    IQR = Q3 - Q1

    # Define the lower and upper bounds for outliers
    lower_bound = Q1 - 3.0 * IQR  # Increase multiplier to 3.0 for more stringent filtering
    upper_bound = Q3 + 3.0 * IQR  # Increase multiplier to 3.0 for more stringent filtering

    # Filter out values outside the bounds (outliers)
    filtered_data = [x for x in data if lower_bound <= x <= upper_bound]

    return filtered_data

def find_worst_cpus(connection, hash_mode, CPUs_speeds):
    # Calculate the first quartile (Q1) and third quartile (Q3)
    CPU_speeds = [speed[3] for speed in CPUs_speeds]

    Q1 = np.percentile(CPU_speeds, 27)
    return database.get_worst_cpus(connection, hash_mode, Q1)

def find_medium_cpus(connection,hash_mode, CPUs_speeds):
    # Calculate the first quartile (Q1) and third quartile (Q3)
    CPU_speeds = [speed[3] for speed in CPUs_speeds]

    Q2_1 = np.percentile(CPU_speeds, 40)
    Q2_2 = np.percentile(CPU_speeds, 60)
    return database.get_medium_cpus(connection, hash_mode, Q2_1, Q2_2)



def create_cpu_boxplots_by_hash(hashmode, CPU_data):
    # Extract CPU names and speeds from the data
    CPU_names = [entry[0] for entry in CPU_data]
    CPU_speeds = [entry[1] for entry in CPU_data]

    # Apply Tukey method to remove outliers
    filtered_speeds = [tukey_method(speeds) for speeds in CPU_speeds]

    # Create a figure for the boxplots
    plt.figure(figsize=(10, 6))
    plt.suptitle(f'Speed Distribution for Hash Mode: {hashmode}', fontsize=16)

    # Create a boxplot for all CPUs with filtered speeds
    plt.boxplot(filtered_speeds, vert=True)
    plt.xticks(range(1, len(CPU_names) + 1), CPU_names, rotation=45, ha='right', fontsize=8)  # Set x-axis labels
    plt.xlabel('CPU Type')
    plt.ylabel('Speed')
    plt.yscale('log')

    # Save the boxplot
    plt.savefig(os.path.join(os.path.dirname(__file__), "..", "plots", "cpus_by_hash", f"cpu_boxplot_{hashmode}.png"))

    # Show the boxplot
    plt.show()

# def create_cpu_iterations_by_hash(hash_mode, iterations, CPU_data):
#     # Extract CPU names and speeds from the data
#     CPU_names = [entry[0] for entry in CPU_data]
#     CPU_speeds = [entry[1] for entry in CPU_data]

#     x_values = list(range(iterations[hash_mode][0], iterations[hash_mode][1] + 1))
#     cpu_y_values = []

#     # Save the subplots
#     output_dir = os.path.join(os.path.dirname(__file__), "..", "plots", "cpus_by_hash")
#     os.makedirs(output_dir, exist_ok=True)
#     plt.savefig(os.path.join(output_dir, f"cpu_boxplot_{hash_mode}.png"))

#     # Show the subplots
#     plt.show()



# Function to create graphs for all CPUs for a given hash mode
def create_cpu_graphs_all_cpus(hash_mode, iterations, cpu_data):
    plt.figure(figsize=(10, 6))
    plt.title(f"Speed vs. Iterations for {hash_mode} (All CPUs)")
    plt.xlabel("Iterations")
    plt.ylabel("Time")
    plt.yscale("log")

    x_values = list(range(iterations[hash_mode][0], iterations[hash_mode][1] + 1))
    y_values_all = {}

    for cpu, speed in cpu_data:
        y_values_temp = {cpu : []}
        for it in x_values:
            cpu_y = (iterations[hash_mode][2] / speed[0]) * it
            y_values_temp[cpu].append(cpu_y)
        y_values_all.update(y_values_temp)

    # for cpu, speed in cpu_data:
    #     speed_function = [(it / iterations[hash_mode][2]) * speed[0] * it for it in iterations[hash_mode]]
    #     plt.plot(range(iterations[hash_mode][0], iterations[hash_mode][1]), speed_function, label=cpu)
    for cpu, y_values in y_values_all.items():
            plt.plot(x_values, y_values, label = cpu)

    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(os.path.dirname(__file__), "..", "plots", "cpus_by_hash", f"cpu_biterations_{hash_mode}.png"))

    # plt.show()


# Function to create a graph for the "medium" CPU for each hash mode
def create_cpu_graph_medium_cpu(iterations, cpu_data, hashes):
    plt.figure(figsize=(10, 6))
    plt.title("Speed vs. Iterations - 'AMD Ryzen 7 4800H'")
    plt.xlabel("Iterations")
    plt.ylabel("Time")
    plt.yscale("log")

    print(cpu_data)

    x_values = list(range(2**0, 2**20))
    y_values_all = {}

    for hash_mode, speed in cpu_data:
        if hash_mode in hashes:
            y_values_temp = {hash_mode : []}
            for it in x_values:
                cpu_y = (iterations[hash_mode][2] / speed[0]) * it
                y_values_temp[hash_mode].append(cpu_y)
            y_values_all.update(y_values_temp)

    for hash_mode, y_values in y_values_all.items():
            plt.plot(x_values, y_values, label = hash_mode)

    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(os.path.dirname(__file__), "..", "plots", "cpus_by_hash", f"cpu_iterations_hashes.png"))

    plt.show()
