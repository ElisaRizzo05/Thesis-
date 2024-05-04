import sqlite3, database, os, json
from GPUs import GPUs_benchmarks, attacker_analysis
from CPUs import CPUs_benchmarks, client_analysis
import GPUs_speeds_data, CPUs_speeds_data, comparison_graphs


gpu_database_entries = []
cpu_database_entries = []
iterations = {"PBKDF2-HMAC-SHA256":[2**0, 2**20, 999], "MD5":[2**0, 2**20, 1], "LM":[2**0, 2**20,1], "SHA2-256":[2**0, 2**20, 1], "SHA3-256":[2**0, 2**20, 1], "scrypt":[2**0, 2**20, 16384], "bcrypt":[2**0, 2**20, 32]}
hashes = ["PBKDF2-HMAC-SHA256", "MD5", "LM", "SHA2-256", "SHA3-256", "scrypt", "bcrypt"]
# "PBKDF2-HMAC-SHA256", "MD5", "LM", "SHA1", "SHA2-256", "SHA2-512", "SHA2-384", "PBKDF2-HMAC-MD5", "PBKDF2-HMAC-SHA1", "SHA3-224", "SHA3-256", "SHA3-384", "SHA3-512"
database_file_path = os.path.join("database", "cpu_gpu_benchmarks.db")


# Function to call all create_table functions
def create_tables(connection):
    database.create_gpu_table(connection)
    database.create_cpu_table(connection)
    database.create_gpu_speeds_table(connection)
    database.create_cpu_speeds_table(connection)


def create_speeds_tables(connection):
    database.create_gpu_speeds_table(connection)
    database.create_cpu_speeds_table(connection)


def populate_speeds_tables(connection):
    # database.insert_gpu_speeds(connection, GPUs_speeds_data.data)
    database.insert_cpu_speeds(connection, CPUs_speeds_data.data)


def populate_tables(connection):
    database.insert_all_gpus(connection)


def empty_tables(connection):
    # database.empty_GPUs_table(connection)
    # database.empty_CPUs_table(connection)
    # database.empty_GPUs_speeds_table(connection)
    database.empty_CPUs_speeds_table(connection)


def drop_tables(connection):
    database.drop_gpus_table(connection)
    database.drop_cpus_table(connection)
    database.drop_gpus_speeds_table(connection)
    database.drop_cpus_speed_table(connection)


def drop_speeds_tables(connection):
    database.drop_gpus_speeds_table(connection)
    database.drop_cpus_speed_table(connection)


def get_GPUs_benchmark_data():
    GPUs_benchmarks.get_all_data(gpu_database_entries)


def get_CPUs_benchmark_data():
    CPUs_benchmarks.get_all_data(cpu_database_entries)


def save_GPUs_speeds_data():
        get_GPUs_benchmark_data()

        # Convert the list to a JSON string
        data_as_json = json.dumps(gpu_database_entries, indent=4)

        # Write the JSON string to the file GPUs_speeds_data.py
        with open(os.path.join(os.path.dirname(__file__), 'GPUs_speeds_data.py'), "w") as file:
            file.write(f"data = {data_as_json}")   


def save_CPUs_speeds_data():
        get_CPUs_benchmark_data()
    
        # Convert the list to a JSON string
        data_as_json = json.dumps(cpu_database_entries, indent=4)

        # Write the JSON string to the file GPUs_speeds_data.py
        with open(os.path.join(os.path.dirname(__file__), 'CPUs_speeds_data.py'), "w") as file:
            file.write(f"data = {data_as_json}")    
        print("done")    


def create_iteration_comparison_graphs(connection, hash_mode):
    GPUs_speeds = database.get_gpus_speeds_by_hash_mode(connection, hash_mode)
    CPUs_speeds = database.get_cpus_speeds_by_hash_mode(connection, hash_mode)
    best_GPUs = attacker_analysis.find_best_gpus(connection, hash_mode, GPUs_speeds)
    worst_CPUs = client_analysis.find_worst_cpus(connection, hash_mode, CPUs_speeds)
    # print(CPUs_speeds)
    return(best_GPUs, worst_CPUs)

def create_medium_iteration_comparison_graphs(connection, hash_mode):
    GPUs_speeds = database.get_gpus_speeds_by_hash_mode(connection, hash_mode)
    CPUs_speeds = database.get_cpus_speeds_by_hash_mode(connection, hash_mode)
    medium_GPUs = attacker_analysis.find_medium_gpus(connection, hash_mode, GPUs_speeds)
    medium_CPUs = client_analysis.find_medium_cpus(connection, hash_mode, CPUs_speeds)
    # print(CPUs_speeds)
    return(medium_GPUs, medium_CPUs)



def create_all_iteration_comparison_graphs(connection):
    best_GPUs = {}
    worst_CPUs = {}
    CPUs = []  # List to store CPUs that appear in all lists
    GPUs = []  # List to store GPUs that appear in all lists

    for hash_mode in hashes:
        best_GPUs[hash_mode], worst_CPUs[hash_mode] = create_iteration_comparison_graphs(connection, hash_mode)

    # Initialize dictionaries to store selected CPU and GPU entries for each hash function
    selected_CPUs = {hash_mode: [] for hash_mode in hashes}
    selected_GPUs = {hash_mode: [] for hash_mode in hashes}

    common_CPUs = set(item[0] for item in worst_CPUs[hash_mode])  # Initialize with the first list
    common_GPUs = set(item[0] for item in best_GPUs[hash_mode])  # Initialize with the first list
    
    # Iterate through each hash function
    for hash_mode in hashes:
        # Find common CPUs among all lists for the current hash function in worst_CPUs
        for cpu_list in worst_CPUs.values():
            common_CPUs.intersection_update(item[0] for item in cpu_list)

        # Find common GPUs among all lists for the current hash function in best_GPUs
        for gpu_list in best_GPUs.values():
            common_GPUs.intersection_update(item[0] for item in gpu_list)

        # Extract entries with common CPU names for the current hash function, selecting the one with the lowest speed and deviation set to 0
        for cpu_name in common_CPUs:
            lowest_speed = float('inf')
            selected_cpu_entry = None
            for cpu_entry in worst_CPUs[hash_mode]:
                if cpu_entry[0] == cpu_name and cpu_entry[1] < lowest_speed and cpu_entry[2] == 0:
                    lowest_speed = cpu_entry[1]
                    selected_cpu_entry = cpu_entry
            if selected_cpu_entry:
                selected_CPUs[hash_mode].append(selected_cpu_entry)

        # Extract entries with common GPU names for the current hash function, selecting the one with the highest speed and deviation set to 0
        for gpu_name in common_GPUs:
            highest_speed = float('-inf')
            selected_gpu_entry = None
            for gpu_entry in best_GPUs[hash_mode]:
                if gpu_entry[0] == gpu_name and gpu_entry[1] > highest_speed and gpu_entry[2] == 0:
                    highest_speed = gpu_entry[1]
                    selected_gpu_entry = gpu_entry
            if selected_gpu_entry:
                selected_GPUs[hash_mode].append(selected_gpu_entry)

   
    # print(common_CPUs)
    # print(common_GPUs)
    for hash_mode in hashes:
        comparison_graphs.create_all_iteration_graphs(hash_mode, iterations, selected_GPUs, selected_CPUs)


def create_all_medium_iteration_comparison_graphs(connection):
    medium_GPUs = {}
    medium_CPUs = {}
    CPUs = []  # List to store CPUs that appear in all lists
    GPUs = []  # List to store GPUs that appear in all lists

    for hash_mode in hashes:
        medium_GPUs[hash_mode], medium_CPUs[hash_mode] = create_medium_iteration_comparison_graphs(connection, hash_mode)

    # Initialize dictionaries to store selected CPU and GPU entries for each hash function
    selected_CPUs = {hash_mode: [] for hash_mode in hashes}
    selected_GPUs = {hash_mode: [] for hash_mode in hashes}

    common_CPUs = set(item[0] for item in medium_CPUs[hash_mode])  # Initialize with the first list
    common_GPUs = set(item[0] for item in medium_GPUs[hash_mode])  # Initialize with the first list

    # Iterate through each hash function
    for hash_mode in hashes:
        # Find common CPUs among all lists for the current hash function in medium_CPUs
        for cpu_list in medium_CPUs.values():
            common_CPUs.intersection_update(item[0] for item in cpu_list)

        # Find common GPUs among all lists for the current hash function in medium_GPUs
        for gpu_list in medium_GPUs.values():
            common_GPUs.intersection_update(item[0] for item in gpu_list)
        
    for hash_mode in hashes:
        # Calculate the median speed for CPUs and GPUs for the current hash function
        median_CPU_speeds = {cpu_entry[0]: cpu_entry[1] for cpu_entry in medium_CPUs[hash_mode]}
        median_GPU_speeds = {gpu_entry[0]: gpu_entry[1] for gpu_entry in medium_GPUs[hash_mode]}


        # Extract entries with common CPU names for the current hash function with medium speed
        for cpu_entry in medium_CPUs[hash_mode]:
            cpu_name = cpu_entry[0]
            if cpu_name in median_CPU_speeds and cpu_entry[1] == median_CPU_speeds[cpu_name] and cpu_name in common_CPUs:
                selected_CPUs[hash_mode].append(cpu_entry)

        # Extract entries with common GPU names for the current hash function with medium speed
        for gpu_entry in medium_GPUs[hash_mode]:
            gpu_name = gpu_entry[0]
            if gpu_name in median_GPU_speeds and gpu_entry[1] == median_GPU_speeds[gpu_name] and gpu_name in common_GPUs:
                selected_GPUs[hash_mode].append(gpu_entry)

        comparison_graphs.create_all_iteration_graphs(hash_mode, iterations, selected_GPUs, selected_CPUs)


def create_comparison_graphs(connection, hash_mode):
    GPUs_speeds = database.get_gpus_speeds_by_hash_mode(connection, hash_mode)
    CPUs_speeds = database.get_cpus_speeds_by_hash_mode(connection, hash_mode)
    comparison_graphs.create_all_graphs(hash_mode, GPUs_speeds, CPUs_speeds)


def create_all_comparison_graphs(connection):
    for hash_mode in hashes:
        create_comparison_graphs(connection, hash_mode)


def create_cpu_boxplots(connection, hash_mode):
    CPUs_speeds = database.get_cpu_data_for_boxplot_graphs(connection, hash_mode) #--> serve per i boxplot, butta lo stesso anche se hanno dimensioni di merda
    client_analysis.create_cpu_boxplots_by_hash(hash_mode, CPUs_speeds)

def create_cpu_iterations(connection, hash_mode):
    CPUs_speeds = database.get_cpu_data_for_iteration_graphs(connection, hash_mode)
    # print("CPUs_speeds: ", CPUs_speeds)
    client_analysis.create_cpu_graphs_all_cpus(hash_mode, iterations, CPUs_speeds)

def create_cpu_hashes(connection):
    CPUs_speeds = database.get_cpu_data_for_hashes_graph(connection, "AMD Ryzen 7 4800H")
    client_analysis.create_cpu_graph_medium_cpu(iterations, CPUs_speeds, hashes)

def create_all_cpu_graphs(connection):
    for hash_mode in hashes:
        # create_cpu_boxplots(connection, hash_mode)
        create_cpu_iterations(connection, hash_mode)
        # create_cpu_hashes(connection)

def create_gpu_boxplots(connection, hash_mode):
    GPUs_speeds = database.get_gpu_data_for_boxplot_graphs(connection, hash_mode) #--> serve per i boxplot, butta lo stesso anche se hanno dimensioni di merda
    attacker_analysis.create_gpu_boxplots_by_hash(hash_mode, GPUs_speeds)

def create_gpu_iterations(connection, hash_mode):
    GPUs_speeds = database.get_gpu_data_for_iteration_graphs(connection, hash_mode)
    # print("GPUs_speeds: ", GPUs_speeds)
    attacker_analysis.create_gpu_graphs_all_gpus(hash_mode, iterations, GPUs_speeds)

def create_gpu_hashes(connection):
    GPUs_speeds = database.get_gpu_data_for_hashes_graph(connection, "NVIDIA GeForce GTX 1080")
    attacker_analysis.create_gpu_graph_medium_cpu(iterations, GPUs_speeds, hashes)

def create_all_gpu_graphs(connection):
    for hash_mode in hashes:
        # create_gpu_boxplots(connection, hash_mode)
        create_gpu_iterations(connection, hash_mode)

# def create_client_graphs(connection, hash_mode):
#     CPUs_speeds = database.get_cpus_speeds_by_hash_mode(connection, hash_mode)
#     # print("lunghezza: ", len(CPUs_speeds))
#     client_analysis.create_cpu_boxplots(CPUs_speeds, hash_mode)

# def client_graphs(connection):
#     for hash_mode in hashes:
#         create_client_graphs(connection, hash_mode)


def main(database_file_path):
    # Create a connection to the SQLite database.
    connection = database.create_connection(database_file_path)

    if connection:
        # Call the drop_gpu_cpu_tables function to drop all the tables.
        # drop_tables(connection)    
        
        # Call the create_all_tables function to create all the tables
        # create_tables(connection)

        #i dati sono i più aggiornati ora nei due file usa quelli epr fare i grafici

        # Decomment to get all data related to GPUs and save them as a list in the file "GPUs_speeds_data.py"
        # save_GPUs_speeds_data()  

        # Decomment to get all data related to CPUs and save them as a list in the file "CPUs_speeds_data.py"
        # save_CPUs_speeds_data() 

        # Decomment to populate the tables GPUs_speeds and CPUs_speeds with the data in the files "GPUs_speeds_data.py" and"CPUs_speeds_data.py"
        # populate_speeds_tables(connection)

        # Decomment to get all the possible combinations of GPUs in a certain budget
        # res = database.get_gpus_prices(connection)
        # GPUs = {}
        # for el in res: 
        #     GPUs[el[0]] = el[1]
        # # print(GPUs)
        # print(attacker_analysis.find_same_GPUs_combinations(1000, GPUs))
        
        # Decomment to create the comparison graphs between CPUs and GPUs for each of the hashes in the 'hashes' array
        # create_all_comparison_graphs(connection)

        # create_all_cpu_boxplots(connection)
        # save_GPUs_speeds_data()
        # save_CPUs_speeds_data()
        # empty_tables(connection)
        # populate_speeds_tables(connection)
        # for hash_mode in hashes:
        # create_all_iteration_comparison_graphs(connection)
        # create_all_medium_iteration_comparison_graphs(connection)

        #for the medium case graphs --> no gpus in the middle what to do?
        # create_all_medium_iteration_comparison_graphs(connection)

        create_all_gpu_graphs(connection)
        # create_all_cpu_graphs(connection)

        # create_all_iteration_comparison_graphs(connection)




if __name__ == "__main__":
    main('database_file_path.db')
