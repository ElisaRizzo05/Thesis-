import requests
import re, os
from bs4 import BeautifulSoup
from . import GPUs_urls

hashes = ["MD5", "SHA1", "BLAKE2b-512", "MD4", "SHA2-224", "SHA2-256", 
          "descrypt, DES (Unix), Traditional DES", "SHA2-512", 
          "bcrypt  (Iterations: 32)", "scrypt (Iterations: 1)", "SHA2-384", 
          "PBKDF2-HMAC-SHA256", "PBKDF2-HMAC-MD5 (Iterations: 999)", 
          "PBKDF2-HMAC-SHA1 (Iterations: 999)", "SHA3-224", "SHA3-256", "SHA3-384", "SHA3-512"]

# # Initialize an empty list to store the extracted GPU data
# gpu_database_entries = []

# Function to append extracted GPU data to the list
def append_gpu_data(res, gpu_database_entries):
    for element in res:
        gpu_database_entries.append(element)

# Function to get data from URLs
def get_data_from_urls(urls, gpu_database_entries):
    # Loop through each URL in the provided list
    for url in urls:
        # Send an HTTP GET request to the URL
        response = requests.get(url["URL"])
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Get the content of the response
            content = response.content
            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(content, "html.parser")
            
            # Check which source URL is being processed
            if urls == GPUs_urls.github:
                # For GitHub source, extract data and analyse it using the appropriate function
                rows = soup.find_all("td", {"class": "blob-code blob-code-inner js-file-line"})
                res = analyse_data_github(rows, url["Hashcat_version"])
                # Append the extracted GPU data to the main list
                append_gpu_data(res, gpu_database_entries)
            
            elif urls == GPUs_urls.onlinehashcrack:
                # For OnlineHashCrack source, extract data and analyse it using the appropriate function
                data = soup.find("pre")
                res = analyse_data_onlinehashcrack(data, url["Hashcat_version"])
                # Append the extracted GPU data to the main list
                append_gpu_data(res, gpu_database_entries)
            
            elif urls == GPUs_urls.openbenchmarking:
                # For OpenBenchmarking source, extract data and analyse it using the appropriate function
                res = analyse_data_openbenchmarking(soup, url["Hashcat_version"])
                # Append the extracted GPU data to the main list
                append_gpu_data(res, gpu_database_entries)
        
        else:
            # If the request was not successful, print an error message
            print("Connection not successful")

# Function to extract the GPU name from row information
def extract_gpu_name(row_text):
    row_text = row_text.split(":")[1].strip()
    if "with" in row_text:
        GPU = row_text.split("with")[0].strip()
    elif "," in row_text:
        GPU = row_text.split(",")[0].strip()
    else:
        GPU = row_text.strip()
    return GPU

# Function to extract GPU speed from row information and hashmode
def extract_gpu_speed(row, hashmode):
    device = row.split("#")[1].split(".")[0]
    if device != "*":
        speed = row.split(":")[1].split(" (")[0].strip()
        if "MH/s" in speed:
            return float(speed.split(" ")[0].strip()) * 1000000
        elif "kH/s" in speed:
            return float(speed.split(" ")[0].strip()) * 1000
        elif "GH/s" in speed:
            return float(speed.split(" ")[0].strip()) * 1000000000
        else:
            return float(speed.split(" ")[0].strip())

# Function to analyse data from OpenBenchmarking source
def analyse_data_openbenchmarking(soup, hashcat_version):
    # Find the table containing the data
    table = soup.find("div", {"class": "div_table"})
    # Get the hashmode from the select option
    hashmode = soup.select_one("select").select("option[selected]")[0].text.split("Benchmark: ")[1]
    # Find all the rows in the table
    rows = table.find_all("div", {"class": "div_table_row"})
    # Initialize an empty list to store the extracted GPU data
    gpu_list = []
    # Loop through each row in the table
    for row in rows:
        # Check if the row contains relevant data (not "Mid-Tier", "Median", or "Low-Tier")
        if all(string not in row.text for string in ["Mid-Tier", "Median", "Low-Tier"]):
            # Extract the row information
            row_info = row.find_all("div", {"class": "div_table_cell"})
            # Extract the GPU name
            GPU = row_info[0].text.strip()

            # Check if the row contains "+/-" deviation information
            if "+/-" in row_info[3].text:
                # Append GPU data with deviation information
                gpu_list.append({"GPU": GPU, "number_GPUs": 1, "deviation": row_info[3].text.split("+/-")[1].strip(), hashmode: row_info[3].text.split("+/-")[0].strip()})
            else:
                # Append GPU data without deviation information
                gpu_list.append({"GPU": GPU, "number_GPUs": 1, "deviation": 0, hashmode: row_info[3].text.strip()})
    return gpu_list


# Function to analyse data from OnlineHashCrack source
def analyse_data_onlinehashcrack(data, hashcat_version):
    # Split the data by lines
    data = data.text.split("\n")
    GPU = hashmode = ""
    count = 0
    # Initialize a list to store the extracted GPU data
    GPU_speeds = {}

    # Loop through each line in the data
    for row in data:
        # Check if the line contains relevant data (not "ATTENTION! CUDA kernel self-test failed")
        if "ATTENTION! CUDA kernel self-test failed" not in row:
            # Check if the line contains GPU information
            if "Device #" in row:
                count += 1
                GPU = row.split(": ")[1].split(",")[0].strip()
                # Check if the GPU is NVIDIA and add "NVIDIA" prefix if needed
                if any(string in GPU for string in ["GeForce", "Tesla", "A100"]) and "NVIDIA" not in GPU:
                    GPU = "NVIDIA " + GPU

            # Check if the line contains hashmode information
            elif row.startswith('* Hash-Mode'):
                hash_mode_match = re.search(r'^\* Hash-Mode \d+ \((.+\)*)\)\s*?\[?.*\]?', row)
                if hash_mode_match:
                    hashmode = hash_mode_match.group(1).strip()
            elif "Hashmode:" in row:
                hashmode = re.search(r'Hashmode: \d+ - (.*)', row).group(1).strip()
            # Check if the line contains GPU speed information
            elif "Speed" in row and "#*" not in row:
                # Extract GPU speed from the row information and hashmode
                speed = extract_gpu_speed(row, hashmode)
                if count > 1:
                    GPU_speeds[hashmode + re.search(r'.*(#\d+).*' , row).group(1)] = speed
                else:
                    GPU_speeds[hashmode] = speed

    result = []
    
    # If there are multiple GPUs with the same name, update the number of GPUs
    for key, value in GPU_speeds.items():
        if "#" in key:
            key = key.split("#")[0]
        result.append({"GPU": GPU, "number_GPUs": 1, "deviation": 0, key: value})
    # return GPU_speeds
    return result


# Function to analyse data from GitHub source
def analyse_data_github(rows, hashcat_version):
    # Initialize an empty list to store the extracted GPU data
    GPU = ""
    GPU_speeds = {}
    hashmode = ""
    count = 0

    # Loop through each row in the provided data
    for row in rows:
        # Check if the row contains relevant data and doesn't contain any unwanted strings
        if "Device #" in row.text and all(string not in row.text for string in ["skipped", "WARNING", "CUDA SDK Toolkit", "ATTENTION", "Skipping", "OpenCL drivers"]):
            count += 1
            # Extract the GPU name
            GPU = extract_gpu_name(row.text)

            # Check if the GPU is NVIDIA and add "NVIDIA" prefix if needed
            if any(string in GPU for string in ["GeForce", "Tesla", "A100", "TITAN"]) and "NVIDIA" not in GPU:
                GPU = "NVIDIA " + GPU
        # Check if the row contains hashmode information
        elif "Hash-Mode " in row.text:
            hashmode = row.text.split("(")[1].split(")")[0]
        elif "Hashmode" in row.text:
            hashmode = row.text.split(" - ")[1].strip()
        elif "Hashtype" in row.text:
            hashmode = row.text.split(":")[1].strip()
        elif "Speed" in row.text and "#*" not in row.text:
            # Extract GPU speed from the row information and hashmode
            speed = extract_gpu_speed(row.text, hashmode)
            if count > 1:
                GPU_speeds[hashmode + re.search(r'.*(#\d+).*' , row.text).group(1)] = speed
            else:
                GPU_speeds[hashmode] = speed
            
    result = []
    # If there are multiple GPUs with the same name, update the number of GPUs
    for key, value in GPU_speeds.items():
        if "#" in key:
            key = key.split("#")[0]
        result.append({"GPU": GPU, "number_GPUs": 1, "deviation": 0, key: value})
    # return GPU_speeds
    return result

# Function to get data from all URLs (GitHub, OnlineHashCrack, OpenBenchmarking)
def get_data_from_all_urls(gpu_database_entries):
    # Call the get_data_from_urls function for each source URL list
    get_data_from_urls(GPUs_urls.github, gpu_database_entries)
    get_data_from_urls(GPUs_urls.onlinehashcrack, gpu_database_entries)
    get_data_from_urls(GPUs_urls.openbenchmarking, gpu_database_entries)

def get_data_from_file(filename):
    with open(filename, 'r') as file:
        text = file.read()

    gpu_entries = []
    GPU = ''
    number_GPUs = 1
    deviation = 0
    hashes = {}
    count = 0

    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if line.startswith('* Device #') and GPU == '':
            if all(string not in line for string in ["skipped", "WARNING", "CUDA"]):
                GPU = line.split(":")[1].split(",")[0].strip()
                
                if "GeForce" in GPU and "NVIDIA" not in GPU:
                    GPU = "NVIDIA " + GPU
        
        elif line.startswith('* Hash-Mode'):
            hash_mode_match = re.search(r'^\* Hash-Mode \d+ \((.+\)*)\)\s*?\[?.*\]?', line)
            if hash_mode_match:
                hash_mode = hash_mode_match.group(1)
        
        elif line.startswith("Hashmode:"):
            hash_mode_match = re.search(r'^Hashmode: \d+ \- (.*)', line)
            if hash_mode_match:
                hash_mode = hash_mode_match.group(1)

        elif line.startswith("Speed"):
                count += 1
                speed_match = re.search(r'Speed\.#\d+.*:\s*([\d.]+\s*[A-Za-z]?H\/s)', line)
                if speed_match:
                    
                    speed = float(speed_match.group(1).split(" ")[0])
                    if "MH/s" in speed_match.group(1):
                        speed *= 1000000
                    elif "kH/s" in speed_match.group(1):
                        speed *= 1000
                    elif "GH/s" in speed_match.group(1):
                        speed *= 1000000000
                    hashes[str(hash_mode + " ROUND" + str(count))] = speed
    
    for key, value in hashes.items():
        if re.search(r'\sROUND\d+$', key):
            key = key.split(" ROUND")[0]
        gpu_entries.append({'GPU':GPU, 'number_GPUs':number_GPUs, 'deviation':deviation, key:value})

    return gpu_entries

def get_data_from_all_files(gpu_database_entries):
    directory_path = os.path.join(os.path.dirname(__file__), 'GPUs_to_parse')
    gpu_entries = []

    for file in os.listdir(directory_path):
        if file.endswith(".txt"):
            file_path = (os.path.join(directory_path, file))
            cpu_entries = get_data_from_file(file_path)

            # For CPUs with number_CPUs = 1 and deviation = 0
            for element in cpu_entries:
                gpu_database_entries.append(element)

# Function to gather data from all URLs and files in the list
def get_all_data(gpu_database_entries):
    get_data_from_all_urls(gpu_database_entries)
    get_data_from_all_files(gpu_database_entries)
