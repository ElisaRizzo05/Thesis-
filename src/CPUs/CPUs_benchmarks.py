import requests
import re, os
from bs4 import BeautifulSoup
from . import CPUs_urls

# List of hash modes considered
hashes = ["MD5", "SHA1", "BLAKE2b-512", "MD4", "SHA2-224", "SHA2-256", 
          "descrypt, DES (Unix), Traditional DES", "SHA2-512", 
          "bcrypt  (Iterations: 32)", "scrypt (Iterations: 1)", "SHA2-384", 
          "PBKDF2-HMAC-SHA256", "PBKDF2-HMAC-MD5 (Iterations: 999)", 
          "PBKDF2-HMAC-SHA1 (Iterations: 999)", "SHA3-224", "SHA3-256", "SHA3-384", "SHA3-512"]


# Function to gather data from a list of URLs and populate the CPUs_speeds database table
def get_data_from_urls(urls, cpu_database_entries):
    for url in urls:
        # Send a GET request to the URL
        response = requests.get(url["URL"])

        # Check if the request was successful
        if response.status_code == 200:
            content = response.content
            soup = BeautifulSoup(content, "html.parser")

            # Check if the URLs correspond to openbenchmarking
            if urls == CPUs_urls.openbenchmarking:
                res = analyse_data_openbenchmarking(soup, url["JTR_version"])
                for element in res:
                    cpu_database_entries.append(element)
        else:
            print("Connection not succesfull")


# Function to analyze data from openbenchmarking URLs
def analyse_data_openbenchmarking(soup, JTR_version):
    table = soup.find("div", {"class": "div_table"})
    hashmode = soup.find("h5").text
    num_CPUs = 1

    # Extraxt the hash mode from the title
    if "Test: " in hashmode:
        hashmode = hashmode.split(":")[1].strip()

    # Inizialization of an ampty list to store CPU information
    cpu_list = []   

#   Iterate through rows in the table
    rows = table.find_all("div", {"class": "div_table_row"})
    for row in rows:
        # Check if the row contains information about the CPU
        if all(string not in row.text for string in ["Mid-Tier", "Median", "Low-Tier"]):
            row_info = row.find_all("div", {"class": "div_table_cell"})
            
            # Extract CPU name
            if "with" in row_info[0].text:
                CPU = row_info[0].text.split("with")[0].strip()
            elif re.search(r'\s[0-9]+-Core', row_info[0].text):
                CPU = re.sub(r'\s[0-9]+-Core', '', row_info[0].text).strip()
            else:
                CPU = row_info[0].text

            # Extract number of CPUs
            if re.search(r'^[0-9]+\sx\s', CPU):
                num_CPUs = CPU.split(' x ')[0].strip()
                CPU = re.sub(r'^[0-9]+\sx\s', '', CPU)

            # Extract hash rate and deviation
            if "+/-" in row_info[3].text:
                cpu_list.append({"CPU": CPU, "number_CPUs": int(num_CPUs), "deviation": float(row_info[3].text.split("+/-")[1].strip()), hashmode: float(row_info[3].text.split("+/-")[0].strip())})
            else:
                cpu_list.append({"CPU": CPU, "number_CPUs": int(num_CPUs), "deviation": 0, hashmode: float(row_info[3].text.strip())})
    return cpu_list


def get_data_from_file(filename):
    with open(filename, 'r') as file:
        text = file.read()

    cpu_entries = []
    CPU = ''
    number_CPUs = 1
    deviation = 0
    hashes = {}
    count = 0

    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if line.startswith('* Device #') and CPU == '':
            if 'Intel' in line:
                match = re.search(r'.*(Intel)\s*(?:\(R\))?\s*(Core)\s*\(TM\)\s*([a-zA-Z0-9-]+)\s*?(CPU)?.*', line)
                if match:
                    CPU = str(match.group(1) + " " + match.group(2) + " "+ match.group(3))
            if 'Ryzen' in line:
                if '-Core' in line and "Device #3:" in line:
                    CPU = re.search(r'\* Device #3: (.*) [A-Za-z]+\-Core', line).group(1)
                if '-Core' in line and "Device #2:" in line:
                    CPU = re.search(r'\* Device #2: (.*) \d+\-Core', line).group(1)
                if 'with' in line:
                    CPU = re.search(r'\* Device #3: (.*) with', line).group(1)
                if '#4' in line :
                    CPU = re.search(r'Device #4: (.*) \d+\-Core', line).group(1)
        
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
        cpu_entries.append({'CPU':CPU, 'number_CPUs':float(number_CPUs), 'deviation':float(deviation), key:float(value)})

    return cpu_entries

def get_data_from_all_files(cpu_database_entries):
    directory_path = os.path.join(os.path.dirname(__file__), 'CPUs_to_parse')
    cpu_entries = []

    for file in os.listdir(directory_path):
        if file.endswith(".txt"):
            file_path = (os.path.join(directory_path, file))
            cpu_entries = get_data_from_file(file_path)

            # For CPUs with number_CPUs = 1 and deviation = 0
            for element in cpu_entries:
                cpu_database_entries.append(element)

# Function to gather data from all URLs and files in the list
def get_all_data(cpu_database_entries):
    # get_data_from_urls(CPUs_urls.openbenchmarking, cpu_database_entries)
    get_data_from_all_files(cpu_database_entries)
