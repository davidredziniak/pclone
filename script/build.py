import json
import re
import sys
import time
import undetected_chromedriver as uc
import os
import dotenv
import traceback
import httpx

from timeit import default_timer as timer
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

# Proxy Settings
PROXY_HOST = ''
PROXY_PORT = ''
PROXY_USER = ''
PROXY_PASS = ''

# OS Settings
linux = False

# PcPartPicker pre-defined mapping
cpu_map = {}
case_map = {}
mobo_map = {}
gpu_map = {}
mem_map = {}

# Define required specifications for PcPartPicker
general = dict.fromkeys(['price', 'case_color', 'wifi'])
processor = dict.fromkeys(['brand', 'full_model_name', 'model', 'model_num', 'cooling'])
storage = dict.fromkeys(['type', 'hdd_size', 'hdd_rpm', 'ssd_size', 'ssd_interface'])
memory = dict.fromkeys(['type', 'size', 'clock', 'amount'])
graphics = dict.fromkeys(['model', 'amount', 'memory', 'cooling'])
power = dict.fromkeys(['wattage'])
expansion = dict.fromkeys(['pcie_x1', 'pcie_x4', 'pcie_x8', 'pcie_x16', 'internal2-5', 'internal3-5', 'external3-5', 'external5-25', 'm2_slots'])

# Define dictionaries required for building
specs = {'general': general, 'processor': processor, 'storage': storage, 'memory': memory, 'graphics': graphics, 'power': power,
             'expansion': expansion}
exact_specs_found = {'cpu': False, 'gpu': False, 'motherboard': False, 'memory': False, 'ssd': False, 'hdd': False, 'cooling': False, 'case': False, 'psu': False}

# Output JSON for use in web app
output_json = {'success': False, 'exactPc': False, 'originalPrice': 0, 'newPrice': 0, 'link': ''}
output_to_console = False

def load_ppp_maps():
    # Load CPU
    with open('./script/pcpartpicker/cpu.txt', 'r') as _:
        for line in _:
            line = line.strip()
            if line:
                key, value = line.split(':')
                cpu_map[str(key)] = str(value)
    # Load Case
    with open('./script/pcpartpicker/case.txt', 'r') as _:
        for line in _:
            line = line.strip()
            if line:
                key, value = line.split(':')
                case_map[str(key)] = str(value)
    # Load Motherboard
    with open('./script/pcpartpicker/motherboard.txt', 'r') as _:
        for line in _:
            line = line.strip()
            if line:
                key, value = line.split(':')
                mobo_map[str(key)] = str(value)
    # Load Memory
    with open('./script/pcpartpicker/memory.txt', 'r') as _:
        for line in _:
            line = line.strip()
            if line:
                key, value = line.split(':')
                mem_map[str(key)] = str(value)
    # Load GPU
    with open('./script/pcpartpicker/gpu.txt', 'r') as _:
        for line in _:
            line = line.strip()
            if line:
                key, value = line.split(':')
                gpu_map[str(key)] = str(value)

def load_env():
    # Load .env environmental variables
    dotenv_file = dotenv.find_dotenv(usecwd=True)
    dotenv.load_dotenv(dotenv_file)

    # Check if a URL was provided
    if len(sys.argv) < 2:
        print('Missing URL.')
        exit(0)
    
    # Set proxy host
    if os.getenv("PROXY_HOST"):
        global PROXY_HOST 
        PROXY_HOST = os.getenv("PROXY_HOST")
    else:
        print("Missing Proxy Host in .env")
        exit()
    
    # Set proxy port
    if os.getenv("PROXY_PORT"):
        global PROXY_PORT 
        PROXY_PORT = os.getenv("PROXY_PORT")
    else:
        print("Missing Proxy Port in .env")
        exit()

    # Set proxy user
    if os.getenv("PROXY_USER"):
        global PROXY_USER
        PROXY_USER = os.getenv("PROXY_USER")
    else:
        print("Missing Proxy User in .env")
        exit()
    
    # Set proxy pass
    if os.getenv("PROXY_PASS"):
        global PROXY_PASS
        PROXY_PASS = os.getenv("PROXY_PASS")
    else:
        print("Missing Proxy Pass in .env")
        exit()

def retrieve_pc_specs(url):
    # Define headers for web requests
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Host': 'www.bestbuy.com',
        'Priority': 'u=0, i',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    }
    
    # Best Buy specific filtering
    cpu_filter = {'cpu': ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', '13th', '14th', 'Generation', '3000', '5000', '7000', '9000', 'Series']}
    gpu_map_fix = {'GeForce RTX 3080': {'': 'GeForce RTX 3080 10GB', '10': 'GeForce RTX 3080 10GB', '12': 'GeForce RTX 3080 12GB LHR'}, 
                    'GeForce RTX 3060': {'': 'GeForce RTX 3060 8GB', '8': 'GeForce RTX 3060 8GB', '12': 'GeForce RTX 3060 12GB'},
                    'GeForce RTX 3050': 'GeForce RTX 3050 6GB',
                    'GeForce GTX 1650': 'GeForce GTX 1650 G5'}

    try:
        global specs
        pro = { 
            "http://"  : "http://" + PROXY_USER + ":" + PROXY_PASS + "@" + PROXY_HOST + ":" + PROXY_PORT
        }
            
        # Send a GET request to the user provided URL
        #res = requests.get(url, headers=headers, verify=True, proxies=pro)
        res = ''
        with httpx.Client(proxy=pro['http://']) as client:
            res = client.get(url, headers=headers, timeout=10)

        # Retrieve Price of PC
        price = re.search('data-testId="customer-price" tabindex="-1"><span aria-hidden="true">\\$(.*?)</span>', res.text).group(1)
        if price == "":
            exit()

        price = float(price.replace(',', ''))
        specs['general']['price'] = price


        # Search for the specifications in JSON format
        json_string = re.search(
            '<script type="application/json" id="shop-specifications-[0-9]*-json">(.*?)</script>',
            res.text, re.IGNORECASE)
        j_obj = json.loads(json_string.group(1))

        # Parse specifications from various categories
        for section in j_obj['specifications']['categories']:
            match section['displayName']:
                # Find Case Color
                case "General":
                    for detail in section['specifications']:
                        match detail['displayName']:
                            case "Color Category":
                                specs['general']['case_color'] = detail['value']
                # Find CPU Specs    
                case "Processor":
                    for detail in section['specifications']:
                        match detail['displayName']:
                            case "Processor Brand":
                                specs['processor']['brand'] = detail['value']
                            case "Processor Model":
                                model = detail['value'].split(' ')
                                for key in cpu_filter['cpu']:
                                    if key in model:
                                        model.remove(key)
                                if "Threadripper" in model:
                                    model.remove('Ryzen')
                                specs['processor']['model'] = ' '.join(model)
                            case "Processor Model Number":
                                if '-' in detail['value']:
                                    specs['processor']['model_num'] = detail['value'].split('-')[-1]
                                else:
                                    specs['processor']['model_num'] = detail['value'].split(' ')[-1]
                # Find SSD / HDD
                case "Storage":
                    for detail in section['specifications']:
                        match detail['displayName']:
                            case "Storage Type":
                                specs['storage']['type'] = detail['value'].strip().split(',')
                            case "Hard Drive Capacity":
                                specs['storage']['hdd_size'] = detail['value'].split(' ')[
                                    0]
                            case "Hard Drive RPM":
                                specs['storage']['hdd_rpm'] = detail['value'].split(' ')[
                                    0]
                            case "Solid State Drive Capacity":
                                specs['storage']['ssd_size'] = detail['value'].split(' ')[
                                    0]
                            case "Solid State Drive Interface":
                                specs['storage']['ssd_interface'] = detail['value'].split(' ')[0]
                # Find RAM Specs
                case "Memory":
                    for detail in section['specifications']:
                        match detail['displayName']:
                            case "System Memory (RAM)":
                                specs['memory']['size'] = detail['value'].split(' ')[0]
                            case "System Memory RAM Speed":
                                specs['memory']['clock'] = detail['value'].split(' ')[
                                    0]
                            case "Type of Memory (RAM)":
                                specs['memory']['type'] = detail['value'].split(' ')[0]
                            case "Number of Memory Sticks Included":
                                specs['memory']['amount'] = detail['value']
                # Find Video Card Specs
                case "Graphics":
                    for detail in section['specifications']:
                        match detail['displayName']:
                            case "Graphics":
                                # Check if it is dual graphics cards
                                if "Dual" in detail['value']:
                                    specs['graphics']['model'] = detail['value'].split(' ', 2)[2]
                                    specs['graphics']['amount'] = 2
                                else:
                                    specs['graphics']['model'] = detail['value'].split(' ', 1)[1]
                                    specs['graphics']['amount'] = 1
                            case "GPU Video Memory (RAM)":
                                specs['graphics']['memory'] = detail['value'].split(' ')[0]
                # Find if PC has WiFi
                case "Connectivity":
                    for detail in section['specifications']:
                        if detail['displayName'] == "Wireless Connectivity":
                            if "Wi-Fi" in detail['value']:
                                specs['general']['wifi'] = True
                # Find CPU/GPU Cooler Type (Liquid/Air)
                case "Cooling":
                    for detail in section['specifications']:
                        match detail['displayName']:
                            case "CPU Cooling System":
                                specs['processor']['cooling'] = detail['value']
                            case "GPU Cooling System":
                                specs['graphics']['cooling'] = detail['value']
                # Find PSU wattage (if specified)
                case "Power":
                    for detail in section['specifications']:
                        if detail['displayName'] == "Power Supply Maximum Wattage":
                            specs['power']['wattage'] = detail['value'].split(' ')[0]
                # Find the types and amounts of PCIe slots and storage bays
                case "Expansion":
                    for detail in section['specifications']:
                        match detail['displayName']:
                            case "Number Of PCI-E x1 Slots":
                                specs['expansion']['pcie_x1'] = detail['value']
                            case "Number Of PCI-E x4 Slots":
                                specs['expansion']['pcie_x4'] = detail['value']
                            case "Number Of PCI-E x8 Slots":
                                specs['expansion']['pcie_x8'] = detail['value']
                            case "Number Of PCI-E x16 Slots":
                                specs['expansion']['pcie_x16'] = detail['value']
                            case "Number Of Internal 2.5\" Bays":
                                specs['expansion']['internal2-5'] = detail['value']
                            case "Number Of Internal 3.5\" Bays":
                                specs['expansion']['internal3-5'] = detail['value']
                            case "Number Of External 3.5 Expansion Bays":
                                specs['expansion']['external3-5'] = detail['value']
                            case "Number Of External 5.25 Expansion Bays":
                                specs['expansion']['external5-25'] = detail['value']
                            case "Number of M.2 Slots":
                                specs['expansion']['m2_slots'] = detail['value']

        # Fix parsed GPUs so it is compatible with PcPartPicker
        gpu_model = specs['graphics']['model']
        gpu_memory = specs['graphics']['memory']
        if gpu_model in gpu_map_fix:
            if type(gpu_map_fix[gpu_model]) is not dict:
                specs['graphics']['model'] = gpu_map_fix[gpu_model]
            else:
                if gpu_memory in gpu_map_fix[gpu_model]:
                    specs['graphics']['model'] = gpu_map_fix[gpu_model][gpu_memory]
                else:
                    specs['graphics']['model'] = gpu_map_fix[gpu_model]['']
        
        # Fix CPU names
        if specs['processor']['brand'] == "Intel":
            specs['processor']['full_model_name'] = specs['processor']['model'] + '-' + specs['processor']['model_num']
        else:
            specs['processor']['full_model_name'] = specs['processor']['model'] + ' ' + specs['processor']['model_num']
        
    except Exception:
        print(traceback.format_exc())
        return False
    
    # Output parsed data (DEV)
    #f = open("Parsed.txt", "w")
    #f.write(json.dumps(specs))
    #f.close()

    if output_to_console:
        print("Successfully parsed PC specifications...")
    return True

# Wait for a webpage to load given the exact element conditions in the parameters
def wait_for_webpage(browser, timeout, type, element, message=""):
    try:
        WebDriverWait(browser, timeout).until(EC.presence_of_element_located((type, element)))
        return True
    except TimeoutException:
        # Quit browser to prevent memory leaks
        quit_browser(browser, message)
        return False
    
# Exit browser helper function
def quit_browser(browser, message=""):
    if message != "" and output_to_console:
        print(message)
    browser.quit()
    exit()

"""
Locate a specified product on a page and click the button to add it to the build.

Args:
    product_type (str): Type of the product being searched (e.g., "CPU").
    url (str): URL of the page to search.
    browser (webdriver): Selenium WebDriver instance.
    product_name (str, optional): Specific name of the product to find. Defaults to None.
    output_to_console (bool, optional): Whether to print messages to the console. Defaults to False.

Returns:
    bool: True if the product is found and added; False otherwise.
"""
def locate_product_and_click(product_type, url, browser, product_name=None, output_to_console=False):
    if output_to_console:
        print(f"Locating {product_type}...", end='')

    # Navigate to the specified URL
    browser.get(url)

    # Wait for the table to load
    try:
        WebDriverWait(browser, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//table[@id='paginated_table']//tbody[@id='category_content']//tr"))
        )
    except TimeoutException:
        if product_type == "CPU":
            quit_browser(browser, "Cannot continue without CPU. Exiting.")
        if output_to_console:
            print(f"Error: Failed to locate compatible {product_type}.")
        return False

    # Locate the list of products in the table
    products = browser.find_elements(By.XPATH, "//table[@id='paginated_table']//tbody[@id='category_content']//tr")
    for product in products:
        # Extract product details
        product_name_in_table = product.find_element(By.TAG_NAME, "p").text
        product_price = product.find_element(By.CLASS_NAME, "td__price").text

        # Match the specific product name if provided
        if product_name and product_name != product_name_in_table:
            continue

        # Otherwise, select the first matching product
        add_button = product.find_element(By.CLASS_NAME, "td__add")
        browser.execute_script("arguments[0].click()", add_button)
        if output_to_console:
            print(" added.")
        return True

    # If no product was added
    if output_to_console:
        print(f"Error: No matching {product_type} found.")
    return False
    
def process_specs(browser, specs):
    # Begin process by going to pcpartpicker build homepage
    browser.get("https://pcpartpicker.com/list")

    # Wait for page load (locates if footer exists in DOM)
    wait_for_webpage(browser, 15, By.CLASS_NAME, "footer__copyright", "Initial page took too much time to load.")

   # Add CPU: Matches CPU generation and selects the listing with a price tag
    cpu_url = f"https://pcpartpicker.com/products/cpu/#s={cpu_map[specs['processor']['model']]}"
    if locate_product_and_click("CPU", cpu_url, browser, product_name=specs['processor']['full_model_name']):
        exact_specs_found['cpu'] = True
        wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add GPU: Matches chipset and finds the cheapest option
    gpu_url = f"https://pcpartpicker.com/products/video-card/#sort=price&c={gpu_map[specs['graphics']['model']]}"
    if locate_product_and_click("GPU", gpu_url, browser):
        exact_specs_found['gpu'] = True
        wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add Memory: Matches clock speed and size
    memory_query = ""
    if specs['memory']['clock']:
        memory_query += f"&S={specs['memory']['clock']}"
    if mem_map.get(specs['memory']['size']):
        memory_query += f"&Z={mem_map[specs['memory']['size']]}"

    memory_url = f"https://pcpartpicker.com/products/memory/#sort=price&R=4,5{memory_query}"
    if locate_product_and_click("Memory", memory_url, browser):
        exact_specs_found['memory'] = True
        wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add Motherboard. Matches M2 Slots, Wifi (Yes/No), PCIe slots
    query_string = ""

    # Define a mapping for expansion slots and their query keys
    expansion_mapping = {
        'pcie_x1': ('B', 6),
        'pcie_x4': ('b', 3),
        'pcie_x8': ('H', 6),
        'pcie_x16': ('h', 8),
        'm2_slots': ('E', 7),
    }

    # Build the query string
    for key, (query_key, value) in expansion_mapping.items():
        if specs['expansion'].get(key) is not None:
            query_string += f'&{query_key}={specs["expansion"][key]},{value}'

    # Add WiFi support condition
    if specs['general'].get('wifi'):
        query_string += '&V=10000,9000,8000,6001,6000,4000'

    # Add memory type query
    memory_type = specs['memory']['type']
    if mobo_map.get(memory_type) is not None:
        query_string += f'&L={mobo_map[memory_type]}'

    url_with_query = 'https://pcpartpicker.com/products/motherboard/#sort=price&L=' + query_string
    if locate_product_and_click('Motherboard', url_with_query, browser):
        exact_specs_found['motherboard'] = True
        wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add SSD: Defaults to m.2 form factor, matches interface and size
    if 'SSD' in specs['storage']['type']:
        ssd_query = "&t=0"
        match specs['storage']['ssd_interface']:
            case "NVMe" | "PCIe":
                ssd_query += "&c1=di_m2.pcie_20_x4,di_m2.pcie_30_x2,di_m2.pcie_30_x4,di_m2.pcie_40_x4,di_m2.pcie_40_x8,di_m2.pcie_50_x2,di_m2.pcie_50_x4"
            case "SATA":
                ssd_query += "&c1=di_m2.sata"
        if specs['storage']['ssd_size']:
            ssd_query += f"&A={specs['storage']['ssd_size']}000000000"

        ssd_url = f"https://pcpartpicker.com/products/internal-hard-drive/#sort=price&R=4,5{ssd_query}"
        if locate_product_and_click("SSD", ssd_url, browser):
            exact_specs_found['ssd'] = True
            wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add HDD: Matches RPM and size
    if 'HDD' in specs['storage']['type'] and specs['storage']['hdd_size']:
        hdd_query = ""
        if specs['storage']['hdd_rpm']:
            hdd_query += f"&t={specs['storage']['hdd_rpm']}"
        if specs['storage']['hdd_size']:
            hdd_query += f"&A={specs['storage']['hdd_size']}000000000"

        hdd_url = f"https://pcpartpicker.com/products/internal-hard-drive/#sort=price&R=4,5{hdd_query}"
        if locate_product_and_click("HDD", hdd_url, browser):
            exact_specs_found['hdd'] = True
            wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add Cooling: Matches cooling type
    cooling_query = "&W=10120,10140,10240,10280,10360,10420" if specs['processor']['cooling'] == "Liquid" else "&W=0"
    cooling_url = f"https://pcpartpicker.com/products/cpu-cooler/#sort=price&R=4,5{cooling_query}"
    if locate_product_and_click("Cooling", cooling_url, browser):
        exact_specs_found['cooling'] = True
        wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add Case
    query_string = ""

    # Add expansion specs to query string
    if specs['expansion']['internal2-5'] is not None:
        query_string += "&K=" + specs['expansion']['internal2-5'] + ",17"
    if specs['expansion']['internal3-5'] is not None:
        query_string += "&J=" + specs['expansion']['internal3-5'] + ",20"
    if specs['expansion']['external3-5'] is not None:
        query_string += "&H=" + specs['expansion']['external3-5'] + ",15"
    if specs['expansion']['external5-25'] is not None:
        query_string += "&G=" + specs['expansion']['external5-25'] + ",12"
    if specs['general']['case_color'] is not None:
        query_string += "&c=" + case_map[specs['general']['case_color']]
    
    url_with_query = "https://pcpartpicker.com/products/case/#sort=price&R=5,4" + query_string
    if locate_product_and_click("Case", url_with_query, browser):
        exact_specs_found['case'] = True
        wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add Power Supply
    # If on home page, get estimated wattage needed to power the PC
    psu_wattage = specs['power']['wattage']
    psu_query = f"&A={psu_wattage}000000000,2000000000000"
    psu_url = f"https://pcpartpicker.com/products/power-supply/#sort=price&R=4,5{psu_query}"
    if locate_product_and_click("PSU", psu_url, browser):
        exact_specs_found['psu'] = True
        wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    #Retrieve new price
    if browser.current_url != "https://pcpartpicker.com/list/":
        browser.get("https://pcpartpicker.com/list/")
        
    wait_for_webpage(browser, 15, By.XPATH, "//tr[@class='tr__total tr__total--final']")

    total = float(
        browser.find_element(By.XPATH, "//tr[@class='tr__total tr__total--final']").text.replace('Total: ', '')[1:])
    result = re.search(
        "pp_partlist_edit\\(\\'([a-zA-Z0-9]*)\\'\\)", browser.page_source)

    found_exact = True
    if False in exact_specs_found.values():
        found_exact = False
    
    link = "https://pcpartpicker.com/list/" + result.group(1)

    # Set output JSON for Next.js
    output_json['success'] = True
    output_json['exactPc'] = found_exact
    output_json['originalPrice'] = float(specs['general']['price'])
    output_json['newPrice'] = float(total)
    output_json['link'] = link

    # Pass information to output to user
    output(float(specs['general']['price']), float(total), link, found_exact)

def output(original_price, new_price, url, found_exact):
    if output_to_console:
        print("\nOriginal: $" + str(original_price))
        if not found_exact:
            print("Your Total so far: $" + str(new_price))
            print("\nCouldn't find all matching specs, unable to accurately calculate difference.")
            print("Feel free to customize:")
            print(url)
        else:
            print("\nOriginal: $" + str(original_price))
            print("Your Total: $" + str(new_price))
            print("Difference: $" + str(round(abs(original_price - new_price), 2)))
            if original_price <= new_price or (original_price - new_price <= 100):
                print('You will likely not save any money building the PC yourself.')
            else:
                print('You can definitely save money building the PC yourself.')
            print('\nFeel free to customize:')
            print(url)
    else:
        print(json.dumps(output_json))

def get_driver():
    prox = PROXY_HOST + ":" + PROXY_PORT
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    chrome_options = uc.options.ChromeOptions()

    proxy_extension_path = os.getcwd() + './script/proxy_ext'
    chrome_options.add_argument("--load-extension=" + proxy_extension_path)
    #chrome_options.add_argument('--headless=new')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("user-agent={}".format(user_agent))
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument(f"--proxy-server={prox}")

    return uc.Chrome(options=chrome_options, driver_executable_path="./drivers/chromedriver-linux64/chromedriver", version_main=126) if linux else uc.Chrome(options=chrome_options)

if __name__ == '__main__':

    try:
        # Load PPP maps
        load_ppp_maps()

        # Load Proxy info from .env
        load_env()
    except Exception:
        print(traceback.format_exc())

    url = str(sys.argv[1])

    if output_to_console:
        print("Your URL is: " + url)
    #start = timer()

    # Parse PC Specs from Bestbuy
    retrieve_pc_specs(url)
    
     # Write background script for extension to file (using updated proxy user + pass)
    if not os.path.isfile("./script/proxy_ext/background.js"):
        try:
            b_js = """chrome.webRequest.onAuthRequired.addListener((details, callback) => {
                callback({
                authCredentials: {
                    username: '""" + PROXY_USER + """',
                    password: '""" + PROXY_PASS + """'
                }
                });
            },
            { urls: ["<all_urls>"] },
            ['asyncBlocking']
            );"""

            f = open("./script/proxy_ext/background.js","w+")
            f.write(b_js)
            f.close()
        except Exception:
            print("Couldn't create chrome extension.")

    # Create web driver
    driver = None
    try:
        driver = get_driver()
        if driver:
            time.sleep(1)
            # Process specifications into PcPartPicker
            process_specs(driver, specs)

            # Quit
            quit_browser(driver)
        else:
            print("Driver could not be created.")
    except Exception:
        print(traceback.format_exc())

    #end = timer()

    # Close Selenium Webdriver
    #if output_to_console:
    #    print('\nTime elapsed: %s seconds.' % str(round(end - start, 2)))
