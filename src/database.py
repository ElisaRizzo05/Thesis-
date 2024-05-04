import sqlite3
from GPUs import GPUs_data 
from CPUs import CPUs_data

# Function to create a connection to the SQLite database.
def create_connection(database_file):
    try:
        # Attempt to connect to the database file.
        connection = sqlite3.connect(database_file)
        return connection
    except sqlite3.Error as e:
        # If there's an error while connecting, print the error message and return None.
        print("Error while connecting to the database:", e)
        return None

# Function to create the 'GPUs' table in the database.
def create_gpu_table(connection):
    try:
        with connection:
            cursor = connection.cursor()

            # Check if the 'GPUs' table already exists
            existing_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='GPUs'").fetchone()
        
            # Execute a CREATE TABLE query to create the 'GPUs' table with specific columns.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS GPUs (
                    GPU_type TEXT NOT NULL PRIMARY KEY,
                    GPU_price INTEGER NOT NULL,
                    GPU_cores INTEGER NOT NULL
                )
            """)

            if existing_table:
                print("Table 'GPUs' already exists")
            else:
                print("Created 'GPUs' table") 
    except sqlite3.Error as e:
        print(e)

# Function to create the 'CPUs' table in the database.
def create_cpu_table(connection):
    try:
        with connection:
            cursor = connection.cursor()

            # Check if the 'GPUs' table already exists
            existing_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='CPUs'").fetchone()

            # Execute a CREATE TABLE query to create the 'CPUs' table with specific columns.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS CPUs (
                    CPU_type TEXT NOT NULL PRIMARY KEY,
                    CPU_price INTEGER NOT NULL,
                    CPU_cores INTEGER NOT NULL,
                    CPU_threads INTEGER NOT NULL
                )
            """)

            if existing_table:
                print("Table 'CPUs' already exists")
            else:
                print("Created 'CPUs' table") 
    except sqlite3.Error as e:
        print(e)

# Function to create the 'GPUs_speeds' table in the database.
def create_gpu_speeds_table(connection):
    try:
        with connection:
            cursor = connection.cursor()

            # Check if the 'GPUs_speeds' table already exists
            existing_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='GPUs_speeds'").fetchone()

            # Execute a CREATE TABLE query to create the 'GPUs_speeds' table with specific columns.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS GPUs_speeds (
                    GPU_type TEXT NOT NULL,
                    number_GPUs INTEGER NOT NULL,
                    hash_mode TEXT NOT NULL,
                    avg_speed INTEGER NOT NULL,
                    deviation INTEGER NOT NULL,
                    FOREIGN KEY (GPU_type) REFERENCES GPUs (GPU_type)
                )
            """)

            if existing_table:
                print("Table 'GPUs_speeds' already exists")
            else:
                print("Created 'GPUs_speeds' table") 
    except sqlite3.Error as e:
        print(e)

# Function to create the 'CPUs_speeds' table in the database.
def create_cpu_speeds_table(connection):
    try:
        with connection:
            cursor = connection.cursor()

            # Check if the 'CPUs_speeds' table already exists
            existing_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='CPUs_speeds'").fetchone()

            # Execute a CREATE TABLE query to create the 'CPUs_speeds' table with specific columns.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS CPUs_speeds (
                    CPU_type TEXT NOT NULL,
                    number_CPUs INTEGER NOT NULL,
                    hash_mode TEXT NOT NULL,
                    avg_speed INTEGER NOT NULL,
                    deviation INTEGER NOT NULL,
                    FOREIGN KEY (CPU_type) REFERENCES CPUs (CPU_type)
                )
            """)

            if existing_table:
                print("Table 'GPUs_speeds' already exists")
            else:
                print("Created 'GPUs_speeds' table")     
    except sqlite3.Error as e:
        print(e)

# Function to insert GPU data into the 'GPUs' table.
def insert_gpu(connection, gpu_type, gpu_price, gpu_cores):
    try:
        with connection:
            cursor = connection.cursor()
            # Execute an INSERT query to add GPU data to the 'GPUs' table.
            cursor.execute("INSERT INTO GPUs (GPU_type, GPU_price, GPU_cores) VALUES (?, ?, ?)", (gpu_type, gpu_price, gpu_cores))
    except sqlite3.Error as e:
        # If there's an error while inserting data, print the error message.
        print("Error while inserting GPU data:", e)

def insert_all_gpus(connection):
    try:
        with connection:
            cursor = connection.cursor()
            
            # Check if the 'GPUs' table is empty
            cursor.execute("SELECT COUNT(*) FROM GPUs")
            row_count = cursor.fetchone()[0]
            
            if row_count == 0:
                # The 'GPUs' table is empty, so insert data
                for key, value in GPUs_data.GPUs_info.items():
                    insert_gpu(connection, key, value[0], value[1])
                print("Successfully populated table 'GPUs'")
            else:
                print("Table 'GPUs' is not empty. Empty it before inserting the data.")
    except sqlite3.Error as e:
        print(e)

# Function to insert CPU data into the 'CPUs' table.
def insert_cpu(connection, cpu_type, cpu_price, cpu_cores, cpu_threads):
    try:
        with connection:
            cursor = connection.cursor()
            # Execute an INSERT query to add CPU data to the 'CPUs' table.
            cursor.execute("INSERT INTO CPUs (CPU_type, CPU_price, CPU_cores, CPU_threads) VALUES (?, ?, ?, ?)", (cpu_type, cpu_price, cpu_cores, cpu_threads))
    except sqlite3.Error as e:
        # If there's an error while inserting data, print the error message.
        print("Error while inserting CPU data:", e)

def insert_all_cpus(connection):
    try:
        with connection:
            cursor = connection.cursor()
            
            # Check if the 'CPUs' table is empty
            cursor.execute("SELECT COUNT(*) FROM CPUs")
            row_count = cursor.fetchone()[0]
            
            if row_count == 0:
                # The 'CPUs' table is empty, so insert data
                for key, value in CPUs_data.CPUs_info.items():
                    insert_gpu(connection, key, value[0], value[1])
                print("Successfully populated table 'CPUs'")
            else:
                print("Table 'CPUs' is not empty. Empty it before inserting the data.")
    except sqlite3.Error as e:
        print(e)


# Function to insert GPU speeds data into the 'GPUs_speeds' table.
def insert_gpu_speeds(connection, gpu_database_entries):
    try:
        with connection:
            cursor = connection.cursor()

            # Check if the 'GPUs_speeds' table is empty
            cursor.execute("SELECT COUNT(*) FROM GPUs_speeds")
            row_count = cursor.fetchone()[0]
            print(row_count)
            if row_count == 0:
                for element in gpu_database_entries:
                    for key in element.keys():
                        if key not in ["GPU", "deviation", "number_GPUs"]:
                            hash_mode = key
                            break
                # Execute a series of INSERT queries to add GPU speeds data to the 'GPUs_speeds' table.
                    cursor.execute("INSERT INTO GPUs_speeds (GPU_type, number_GPUs, hash_mode, avg_speed, deviation) VALUES (?, ?, ?, ?, ?)", (element["GPU"], element["number_GPUs"], hash_mode, element[hash_mode], element["deviation"]))
                print("Inserted GPU speeds data into the table")
            else:
                print("Table 'GPUs_speeds' is not empty. Empty it before inserting the data.")
            
    except sqlite3.Error as e:
        print(e)

# Function to insert CPU speeds data into the 'CPUs_speeds' table.
def insert_cpu_speeds(connection, cpu_database_entries):
    try:
        with connection:
            cursor = connection.cursor()

            # Check if the 'CPUs' table is empty
            cursor.execute("SELECT COUNT(*) FROM CPUs_speeds")
            row_count = cursor.fetchone()[0]
            print(row_count)
            if row_count == 0:
                for element in cpu_database_entries:
                    for key in element.keys():
                        if key not in ["CPU", "deviation", "number_CPUs"]:
                            hash_mode = key
                            break
                # Execute a series of INSERT queries to add CPU speeds data to the 'CPUs_speeds' table.
                    cursor.execute("INSERT INTO CPUs_speeds (CPU_type, number_CPUs, hash_mode, avg_speed, deviation) VALUES (?, ?, ?, ?, ?)", (element["CPU"], element["number_CPUs"], hash_mode, element[hash_mode], element["deviation"]))
                print("Inserted CPU speeds data into the table")
            else:
                print("Table 'CPUs_speeds' is not empty. Empty it before inserting the data.")
    except sqlite3.Error as e:
        print(e)

# Function to retrieve all GPU data from the 'GPUs' table.
def get_all_gpus(connection):
    try:
        with connection:
            cursor = connection.cursor()
            # Execute a SELECT query to get all data from the 'GPUs' table.
            cursor.execute("SELECT * FROM GPUs")
            data = cursor.fetchall()
            return data
    except sqlite3.Error as e:
        # If there's an error while retrieving data, print the error message and return an empty list.
        print("Error while retrieving GPU data:", e)
        return []

# Function to retrieve all CPU data from the 'CPUs' table.
def get_all_cpus(connection):
    try:
        with connection:
            cursor = connection.cursor()
            # Execute a SELECT query to get all data from the 'CPUs' table.
            cursor.execute("SELECT * FROM CPUs")
            data = cursor.fetchall()
            return data
    except sqlite3.Error as e:
        # If there's an error while retrieving data, print the error message and return an empty list.
        print("Error while retrieving CPU data:", e)
        return []
    
# Function to retrieve all GPU type and price from the 'GPUs' table.
def get_gpus_prices(connection):
    try:
        with connection:
            cursor = connection.cursor()
            # Execute a SQL query to fetch GPU_type and GPU_price from the GPUs table
            cursor.execute("SELECT GPU_type, GPU_price FROM GPUs")
            data = cursor.fetchall()
            return data
    except sqlite3.Error as e:
        # If there's an error while retrieving data, print the error message and return an empty list.
        print("Error while retrieving GPU data:", e)
        return []
    
def get_all_gpus_speeds(connection):
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM GPUs_speeds")
            data = cursor.fetchall()
            return data
    except sqlite3.Error as e:
        # If there's an error while retrieving data, print the error message and return an empty list.
        print("Error while retrieving GPU speed data:", e)
        return []     
    
def get_all_cpus_speeds(connection):
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM CPUs_speeds")
            data = cursor.fetchall()
            return data
    except sqlite3.Error as e:
        # If there's an error while retrieving data, print the error message and return an empty list.
        print("Error while retrieving CPU speed data:", e)
        return []     

def get_gpus_speeds_by_hash_mode(connection, hash_mode):
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM GPUs_speeds WHERE hash_mode=?", (hash_mode,))
            data = cursor.fetchall()
            return data
    except sqlite3.Error as e:
        # If there's an error while retrieving data, print the error message and return an empty list.
        print("Error while retrieving entries by hash_mode:", e)
        return []

def get_cpus_speeds_by_hash_mode(connection, hash_mode):
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM CPUs_speeds WHERE hash_mode=?", (hash_mode,))
            data = cursor.fetchall()
            return data
    except sqlite3.Error as e:
        # If there's an error while retrieving data, print the error message and return an empty list.
        print("Error while retrieving entries by hash_mode:", e)
        return []

def get_gpu_data_for_graphs(connection):
    try:
        with connection:
            cursor = connection.cursor()
            
            # Select GPU_type, avg_speed, and deviation columns from the 'GPUs_speeds' table
            cursor.execute("SELECT GPU_type, GROUP_CONCAT(avg_speed), GROUP_CONCAT(deviation) FROM GPUs_speeds GROUP BY GPU_type")

            # Fetch all rows from the result set
            rows = cursor.fetchall()

            # Convert the SQL result to the desired format
            gpu_data = [(row[0], [int(speed) for speed in row[1].split(',')], [int(deviation) for deviation in row[2].split(',')]) for row in rows]

        return gpu_data

    except sqlite3.Error as e:
        print("Error while retrieving entries:", e)
        return []


def get_cpu_data_for_boxplot_graphs(connection, hash_mode):
    try:
        with connection:
            cursor = connection.cursor()
            
            # Select CPU_type, avg_speed, and deviation columns from the 'CPUs_speeds' table
            cursor.execute("SELECT CPU_type, GROUP_CONCAT(avg_speed) FROM CPUs_speeds WHERE hash_mode = ? GROUP BY CPU_type", (hash_mode,))

            # Fetch all rows from the result set
            rows = cursor.fetchall()
            print(rows)
            # Convert the SQL result to the desired format
            cpu_data = [(row[0], [float(speed) for speed in row[1].split(',')]) for row in rows]
        return cpu_data

    except sqlite3.Error as e:
        print("Error while retrieving entries:", e)
        return []
    
def get_cpu_data_for_iteration_graphs(connection, hash_mode):
    try:
        with connection:
            cursor = connection.cursor()
            
            # Select CPU_type, avg_speed, and deviation columns from the 'CPUs_speeds' table
            cursor.execute("SELECT CPU_type, AVG(avg_speed), hash_mode FROM CPUs_speeds WHERE hash_mode = ? GROUP BY CPU_type", (hash_mode,))

            # Fetch all rows from the result set
            rows = cursor.fetchall()
            # print(rows)
            # Convert the SQL result to the desired format
            cpu_data = [(row[0], [float(row[1])]) for row in rows]
        return cpu_data

    except sqlite3.Error as e:
        print("Error while retrieving entries:", e)
        return []
    
def get_cpu_data_for_hashes_graph(connection, cpu):
    try: 
        with connection:
            cursor = connection.cursor()

            cursor.execute("SELECT hash_mode, AVG(avg_speed) FROM CPUs_speeds WHERE CPU_type = ? GROUP BY hash_mode", (cpu,))

            # Fetch all rows from the result set
            rows = cursor.fetchall()
            # print(rows)
            # Convert the SQL result to the desired format
            cpu_data = [(row[0], [float(row[1])]) for row in rows]
        return cpu_data

    except sqlite3.Error as e:
        print("Error while retrieving entries:", e)
        return []

def get_gpu_data_for_hashes_graph(connection, gpu):
    try: 
        with connection:
            cursor = connection.cursor()
            
            cursor.execute("SELECT hash_mode, AVG(avg_speed) FROM GPUs_speeds WHERE GPU_type = ? GROUP BY hash_mode", (gpu,))

            # Fetch all rows from the result set
            rows = cursor.fetchall()
            # print(rows)
            # Convert the SQL result to the desired format
            gpu_data = [(row[0], [float(row[1])]) for row in rows]
        return gpu_data

    except sqlite3.Error as e:
        print("Error while retrieving entries:", e)
        return []

def get_gpu_data_for_iteration_graphs(connection, hash_mode):
    try:
        with connection:
            cursor = connection.cursor()
            
            # Select CPU_type, avg_speed, and deviation columns from the 'CPUs_speeds' table
            cursor.execute("SELECT GPU_type, AVG(avg_speed), hash_mode FROM GPUs_speeds WHERE hash_mode = ? GROUP BY GPU_type", (hash_mode,))

            # Fetch all rows from the result set
            rows = cursor.fetchall()
            # print(rows)
            # Convert the SQL result to the desired format
            gpu_data = [(row[0], [float(row[1])]) for row in rows]
        return gpu_data

    except sqlite3.Error as e:
        print("Error while retrieving entries:", e)
        return []

def empty_GPUs_table(connection):
    try:
        with connection:
            cursor = connection.cursor()
            
            # Check if the table is empty
            cursor.execute("SELECT COUNT(*) FROM GPUs")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("The 'GPUs' table is already empty.")
            else:
                # Execute a DELETE statement to remove all rows from the 'GPUs' table
                cursor.execute("DELETE FROM GPUs")
                print("Emptied 'GPUs' table")
    except sqlite3.Error as e:
        print(e)

def empty_CPUs_table(connection):
    try:
        with connection:
            cursor = connection.cursor()
            
            # Check if the table is empty
            cursor.execute("SELECT COUNT(*) FROM CPUs")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("The 'CPUs' table is already empty.")
            else:
                # Execute a DELETE statement to remove all rows from the 'CPUs' table
                cursor.execute("DELETE FROM CPUs")
                print("Emptied 'CPUs' table")
    except sqlite3.Error as e:
        print(e)

def empty_GPUs_speeds_table(connection):
    try:
        with connection:
            cursor = connection.cursor()
            
            # Check if the table is empty
            cursor.execute("SELECT COUNT(*) FROM GPUs_speeds")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("The 'GPUs_speeds' table is already empty.")
            else:
                # Execute a DELETE statement to remove all rows from the 'GPUs_speeds' table
                cursor.execute("DELETE FROM GPUs_speeds")
                print("Emptied 'GPUs_speeds' table")
    except sqlite3.Error as e:
        print(e)

def empty_CPUs_speeds_table(connection):
    try:
        with connection:
            cursor = connection.cursor()
            
            # Check if the table is empty
            cursor.execute("SELECT COUNT(*) FROM CPUs_speeds")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("The 'CPUs_speeds' table is already empty.")
            else:
                # Execute a DELETE statement to remove all rows from the 'CPUs_speeds' table
                cursor.execute("DELETE FROM CPUs_speeds")
                print("Emptied 'CPUs_speeds' table")
    except sqlite3.Error as e:
        print(e)

# Function to drop the 'GPUs' table from the database.
def drop_gpus_table(connection):
    try:
        with connection:
            cursor = connection.cursor()
            
            # Check if the 'GPUs' table already exists
            existing_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='GPUs'").fetchone()

            if existing_table:
                # Execute a DROP TABLE query to remove the 'GPUs' table from the database.
                cursor.execute("DROP TABLE GPUs")

                print("Table 'GPUs' dropped")
            else:
                print("Table 'GPUs' didn't exist")
    except sqlite3.Error as e:
        # If there's an error while dropping the table, print the error message.
        print(e)

# Function to drop the 'GPUs_speeds' table from the database.
def drop_gpus_speeds_table(connection):
    try:
        with connection:
            cursor = connection.cursor()
        
            # Check if the 'GPUs_speeds' table already exists
            existing_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='GPUs_speeds'").fetchone()

            if existing_table:
                # Execute a DROP TABLE query to remove the 'GPUs_speeds' table from the database.
                cursor.execute("DROP TABLE GPUs_speeds")

                print("Table 'GPUs_speeds' dropped")
            else:
                print("Table 'GPUs_speeds' didn't exist")
    except sqlite3.Error as e:
        # If there's an error while dropping the table, print the error message.
        print(e)

# Function to drop the 'CPUs' table from the database.
def drop_cpus_table(connection):
    try:
        with connection:
            cursor = connection.cursor()

            # Check if the 'CPUs' table already exists
            existing_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='CPUs'").fetchone()

            if existing_table:

                # Execute a DROP TABLE query to remove the 'CPUs' table from the database.
                cursor.execute("DROP TABLE CPUs")

                print("Table 'CPUs' dropped")
            else:
                print("Table 'CPUs' didn't exist")
    except sqlite3.Error as e:
        # If there's an error while dropping the table, print the error message.
        print(e)

# Function to drop the 'CPUs_speeds' table from the database.
def drop_cpus_speed_table(connection):
    try:
        with connection:
            cursor = connection.cursor()

            # Check if the 'CPUs_speeds' table already exists
            existing_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='CPUs_speeds'").fetchone()

            if existing_table:
                # Execute a DROP TABLE query to remove the 'CPUs_speeds' table from the database.
                cursor.execute("DROP TABLE CPUs_speeds")

                print("Table 'CPUs_speeds' dropped")
            else:
                print("Table 'CPUs_speeds' didn't exist")
    except sqlite3.Error as e:
        # If there's an error while dropping the table, print the error message.
        print(e)

def get_best_gpus(connection, hash_mode, quartile):
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT GPU_type, avg_speed, deviation FROM GPUs_speeds WHERE hash_mode=? AND avg_speed > ?", (hash_mode, quartile))
            data = cursor.fetchall()
            return data
    except sqlite3.Error as e:
        # If there's an error while retrieving data, print the error message and return an empty list.
        print("Error while retrieving entries by hash_mode:", e)
        return []

def get_medium_gpus(connection, hash_mode, quartile_1, quartile_2):
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT GPU_type, avg_speed, deviation FROM GPUs_speeds WHERE hash_mode=? AND avg_speed >= ? AND avg_speed <= ?", (hash_mode, quartile_1, quartile_2))
            data = cursor.fetchall()
            return data
    except sqlite3.Error as e:
        # If there's an error while retrieving data, print the error message and return an empty list.
        print("Error while retrieving entries by hash_mode:", e)
        return []


def get_worst_cpus(connection, hash_mode, quartile):
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT CPU_type, avg_speed, deviation FROM CPUs_speeds WHERE hash_mode=? AND avg_speed < ?", (hash_mode, quartile))
            data = cursor.fetchall()
            return data
    except sqlite3.Error as e:
        # If there's an error while retrieving data, print the error message and return an empty list.
        print("Error while retrieving entries by hash_mode:", e)
        return []

def get_medium_cpus(connection, hash_mode, quartile_1, quartile_2):
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT CPU_type, avg_speed, deviation FROM CPUs_speeds WHERE hash_mode=? AND avg_speed >= ? AND avg_speed <= ?", (hash_mode, quartile_1, quartile_2))
            data = cursor.fetchall()
            return data
    except sqlite3.Error as e:
        # If there's an error while retrieving data, print the error message and return an empty list.
        print("Error while retrieving entries by hash_mode:", e)
        return []
