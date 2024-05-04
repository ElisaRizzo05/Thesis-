from itertools import combinations_with_replacement
import matplotlib.pyplot as plt
import os
import numpy as np
import database
from sklearn.cluster import KMeans

def same_GPUs_combinations(budget, GPUs):
    combinations = []  # List to store the valid combinations of GPUs
    
    for GPU_name, GPU_speed in GPUs.items():
        max_repeats = budget // GPU_speed  # Calculate the maximum number of times the GPU can be repeated
        for repeats in range(max_repeats + 1):
            if repeats == 0:
                continue  # Skip combinations with zero GPUs
            combination_cost = repeats * GPU_speed
            if combination_cost <= budget:
                # Generate all combinations with the same GPU type and within budget
                GPU_combinations = combinations_with_replacement([GPU_name], repeats)
                combinations.extend(GPU_combinations)
    
    # Format the combinations as strings
    formatted_combinations = [", ".join(combination) if len(combination) > 1 else combination[0] for combination in combinations]
    
    return formatted_combinations

# Wrapper function to find GPU combinations with the same GPU repeated 'n' times within a specified budget
def find_same_GPUs_combinations(budget_at_disposal, GPUs):
    # Call the find_combinations_within_budget function with the provided budget
    return same_GPUs_combinations(budget_at_disposal, GPUs)

def find_best_gpus(connection, hash_mode, GPUs_speeds):
    # Calculate the third quartile (Q3)
    GPU_speeds = [speed[3] for speed in GPUs_speeds]

    Q3 = np.percentile(GPU_speeds, 70)
    return database.get_best_gpus(connection, hash_mode, Q3)

def find_medium_gpus(connection, hash_mode, GPUs_speeds):
    # Calculate the third quartile (Q3)
    GPU_speeds = [speed[3] for speed in GPUs_speeds]

    Q2_1 = np.percentile(GPU_speeds, 23)
    Q2_2 = np.percentile(GPU_speeds, 77)
    print(hash_mode, Q2_1, Q2_2, np.percentile(GPU_speeds, 50))
    return database.get_medium_gpus(connection, hash_mode, Q2_1, Q2_2)


# Function to create graphs for all CPUs for a given hash mode
def create_gpu_graphs_all_gpus(hash_mode, iterations, gpu_data):
    plt.figure(figsize=(10, 6))
    plt.title(f"Speed vs. Iterations for {hash_mode} (All GPUs)")
    plt.xlabel("Iterations")
    plt.ylabel("Time")
    plt.yscale("log")

    x_values = list(range(iterations[hash_mode][0], iterations[hash_mode][1] + 1))
    y_values_all = {}

    for gpu, speed in gpu_data:
        y_values_temp = {gpu : []}
        for it in x_values:
            gpu_y = (iterations[hash_mode][2] / speed[0]) * it
            y_values_temp[gpu].append(gpu_y)
        y_values_all.update(y_values_temp)

    for gpu, y_values in y_values_all.items():
        plt.plot(x_values, y_values, label = gpu)

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=len(gpu_data))
    plt.grid(True)
    plt.savefig(os.path.join(os.path.dirname(__file__), "..", "plots", "gpus_by_hash", f"gpu_biterations_{hash_mode}.png"))

    plt.show()

# Function to create a graph for the "medium" CPU for each hash mode
def create_gpu_graph_medium_cpu(iterations, gpu_data, hashes):
    plt.figure(figsize=(10, 6))
    plt.title("Speed vs. Iterations - 'NVIDIA GeForce GTX 1080'")
    plt.xlabel("Iterations")
    plt.ylabel("Time")
    plt.yscale("log")

    # print(gpu_data)

    x_values = list(range(2**0, 2**20))
    y_values_all = {}

    for hash_mode, speed in gpu_data:
        if hash_mode in hashes:
            y_values_temp = {hash_mode : []}
            for it in x_values:
                gpu_y = (iterations[hash_mode][2] / speed[0]) * it
                y_values_temp[hash_mode].append(gpu_y)
            y_values_all.update(y_values_temp)

    for hash_mode, y_values in y_values_all.items():
            plt.plot(x_values, y_values, label = hash_mode)

    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(os.path.dirname(__file__), "..", "plots", "gpus_by_hash", f"gpu_iterations_hashes.png"))

    plt.show()
