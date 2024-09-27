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
linux = True

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
    """
    Loads data from five text files into dictionaries (`cpu_map`, `case_map`,
    `mobo_map`, `mem_map`, and `gpu_map`). The data is read line by line, stripped
    of leading/trailing whitespace, and split into key-value pairs.

    """
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
    """
    Loads environment variables from a `.env` file, checks for required command-line
    arguments and proxy settings, and sets global variables based on these
    configurations if they exist. It exits with an error message if any setting
    is missing.

    """
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
    """
    Scrapes product details from a Best Buy webpage, parsing general information
    such as price and technical specs like processor model, memory, graphics card,
    storage, and cooling systems into a structured dictionary called `specs`.

    Args:
        url (str): Expected to be a URL that corresponds to a product page on
            bestbuy.com, from which PC specifications will be retrieved.

    Returns:
        bool: True upon successful parsing and extraction of PC specifications
        from a given URL, and False otherwise. The extracted specs are stored
        globally in the 'specs' dictionary.

    """
    # Define headers for web requests
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.8',
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
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
            res = client.get(url, headers=headers, timeout=None)

        # Retrieve Price of PC
        price = re.search(
            'data-testId="customer-price" tabindex="-1"><span aria-hidden="true">\\$(.*?)</span>', res.text).group(1)
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
def wait_for_webpage(browser, timeout, type, element):
    """
    Uses Selenium WebDriver to wait for a specified element on a webpage to become
    visible within a given timeout period. It returns True if the element is found
    before the timeout, and False otherwise.

    Args:
        browser (WebDriver | SeleniumRemoteConnection): Presumably an instance of
            a web browser automation interface, such as ChromeDriver or FirefoxDriver,
            used for interacting with a webpage.
        timeout (int): 1: used to specify a maximum wait duration in seconds for
            an element to become visible on the webpage.
        type (By): Used to locate an element on a web page using Selenium WebDriver's
            By class, which provides methods to specify how elements are located
            by the driver.
        element (By): Passed to the `EC.presence_of_element_located()` method,
            which expects a tuple containing a By type and an element identifier
            as arguments.

    Returns:
        bool: True when the element is found within the specified timeout, and
        False otherwise, indicating a timeout exception occurred or an error
        occurred while waiting for the webpage to load.

    """
    try:
        WebDriverWait(browser, timeout).until(EC.presence_of_element_located((type, element)))
        return True
    except TimeoutException:
        if output_to_console:
            print("Loading took too much time!")
        return False
    
# Exit browser helper function
def quit_browser(browser, message=""):
    """
    Closes a web browser session. It takes two arguments: `browser`, which is an
    instance of a web browser, and `message`, an optional string to print before
    quitting. If `message` is not empty, it prints the message before closing the
    browser.

    Args:
        browser (Browser | None): Required to be provided by the caller, indicating
            that it represents an instance of a web browser being controlled by
            automation software.
        message (str | None): 0 by default. It specifies an optional message to
            be printed before closing the browser, which can be customized using
            string input.

    """
    if message != "":
        print(message)
    browser.quit()

# Find a (specified) product and clicks button to add to the build
def locate_product_and_click(name, url, browser, product_name = None):
    """
    Navigates to a webpage, locates an element with specific data based on name
    or product ID, clicks the "add" button for that product, and returns True upon
    successful execution. It handles exceptions for timeouts and incompatible products.

    Args:
        name (str | None): Used to display a message to the console during product
            locating, specifying what product is being located. It defaults to
            None if not provided.
        url (str): Expected to be a web URL that the browser will navigate to in
            order to locate the product specified by the other parameters.
        browser (WebDriver): Presumably an instance of a class that represents a
            web browser, allowing it to interact with the web page being navigated.
        product_name (str | None): Optional by default. It specifies the name of
            the product to locate and add, allowing for a specific product to be
            targeted instead of all matching products.

    Returns:
        bool: True when a product is successfully located and added to cart,
        otherwise it returns False due to timeout or other issues.

    """
    if output_to_console:
        print("Locating %s..." % name, end='')

    # Go to URL
    browser.get(url)

    # Wait until table is loaded
    try:
        WebDriverWait(browser, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//table[@id='paginated_table']//tbody[@id='category_content']//tr")))
    except TimeoutException:
        if name == "CPU":
            print("Cannot continue without CPU.. Exiting")
            browser.quit()
            exit()
        # No product was found
        if output_to_console:
            print("Error finding compatible " + name)
        return False
    
    # Locate a list of products
    products = browser.find_elements(By.XPATH, "//table[@id='paginated_table']//tbody[@id='category_content']//tr")
    for product in products:
        # Extract name of product
        name = product.find_element(By.TAG_NAME, "p").text
        price = product.find_element(By.CLASS_NAME, "td__price")
            
        # Match exact product name if parameter is given
        if product_name is not None and name != product_name:
            continue
        else:
            # Match first product
            button = product.find_element(By.CLASS_NAME, "td__add")
            browser.execute_script("arguments[0].click()", button)
            if output_to_console:
                print("added")
            return True
    
def process_specs(browser, specs):
    """
    Automates PC part selection on pcpartpicker.com by filtering components based
    on user-specified specifications and creating a custom build list with estimated
    costs. It extracts component links, prices, and exact matches found.

    Args:
        browser (WebDriver): Used to interact with a web browser for automation
            purposes such as navigating URLs and locating elements on the webpage.
        specs (Dict[str, Any | List[Any]]): Used to represent system specifications
            for building or purchasing. It contains key-value pairs describing
            various components such as processor, memory, storage, cooling, power
            supply, motherboard, case, etc.

    """
    # Begin process by going to pcpartpicker build homepage
    browser.get("https://pcpartpicker.com/list")

    # Wait for page load (locates if footer exists in DOM)
    if not wait_for_webpage(browser, 15, By.CLASS_NAME, "footer__copyright"):
        quit_browser(browser, "Webpage did not load. Exiting")

    # Add CPU. Matches CPU generation and picks listing with a price tag.
    url_with_query = "https://pcpartpicker.com/products/cpu/#s=" + cpu_map[specs['processor']['model']]

    # Locate product, if found wait until /list loads
    if locate_product_and_click("CPU", url_with_query, browser, product_name=specs['processor']['full_model_name']):
        exact_specs_found['cpu'] = True
        wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add GPU. Matches chipset and finds cheapest card.
    url_with_query = "https://pcpartpicker.com/products/video-card/#sort=price&c=" + gpu_map[specs['graphics']['model']]
    if locate_product_and_click("GPU", url_with_query, browser):
        exact_specs_found['gpu'] = True
        wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add Motherboard. Matches M2 Slots, Wifi (Yes/No), PCIe slots
    query_string = ""

    if specs['expansion']['pcie_x1'] is not None:
        query_string += ('&B=%s,6' % specs['expansion']['pcie_x1'])
    if specs['expansion']['pcie_x4'] is not None:
        query_string += ('&b=%s,3' % specs['expansion']['pcie_x4'])
    if specs['expansion']['pcie_x8'] is not None:
        query_string += ('&H=%s,6' % specs['expansion']['pcie_x8'])
    if specs['expansion']['pcie_x16'] is not None:
        query_string += ('&h=%s,8' % specs['expansion']['pcie_x16'])
    if specs['expansion']['m2_slots'] is not None:
        query_string += ('&E=%s,7' % specs['expansion']['m2_slots'])
    if specs['general']['wifi'] is True:
        query_string += '&V=10000,9000,8000,6001,6000,4000'
    if mobo_map[specs['memory']['type']] is not None:
        query_string += '&L=%s' % mobo_map[specs['memory']['type']]

    url_with_query = 'https://pcpartpicker.com/products/motherboard/#sort=price&L=' + query_string
    if locate_product_and_click('Motherboard', url_with_query, browser):
        exact_specs_found['motherboard'] = True
        wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add Memory
    query_string = ""

    if specs['memory']['clock'] is not None:
        query_string += '&S=%s' % specs['memory']['clock']
    if mem_map[specs['memory']['size']] is not None:
        query_string += "&Z=" + mem_map[specs['memory']['size']]

    url_with_query = "https://pcpartpicker.com/products/memory/#sort=price&R=4,5" + query_string
    if locate_product_and_click('Memory', url_with_query, browser):
        exact_specs_found['memory'] = True
        wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add SSD, default to m2 form factor
    if 'SSD' in specs['storage']['type']:
        query_string = "&t=0"

        # If NVMe protocol is specified, it is PCIe interface
        if specs['storage']['ssd_interface'] == "NVMe":
            query_string += "&D=1&c1=di_m2.pcie_20_x4,di_m2.pcie_30_x2,di_m2.pcie_30_x4,di_m2.pcie_40_x4,di_m2.pcie_40_x8,di_m2.pcie_50_x2,di_m2.pcie_50_x4"

        
        match specs['storage']['ssd_interface']:
            case "NVMe":
                query_string += "&D=1&c1=di_m2.pcie_20_x4,di_m2.pcie_30_x2,di_m2.pcie_30_x4,di_m2.pcie_40_x4,di_m2.pcie_40_x8,di_m2.pcie_50_x2,di_m2.pcie_50_x4"
            case "PCIe":
                query_string += "&c1=di_m2.pcie_20_x4,di_m2.pcie_30_x2,di_m2.pcie_30_x4,di_m2.pcie_40_x4,di_m2.pcie_40_x8,di_m2.pcie_50_x2,di_m2.pcie_50_x4"
            case 'SATA':
                query_string += "&c1=di_m2.sata"
            case _:
                if output_to_console:
                    print("Couldn't find exact SSD interface... choosing a random compatible product")


        if specs['storage']['ssd_size'] is not None:
            query_string += "&A=" + specs['storage']['ssd_size'] + "000000000"

        url_with_query = "https://pcpartpicker.com/products/internal-hard-drive/#sort=price&R=4,5" + query_string
        if locate_product_and_click('SSD', url_with_query, browser):
            exact_specs_found['ssd'] = True
            wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add HDD
    if 'HDD' in specs['storage']['type'] and specs['storage']['hdd_size'] is not ('0' or None):
        query_string = ""
        if specs['storage']['hdd_rpm'] is not None:
            query_string += '&t=' + specs['storage']['hdd_rpm']
        if specs['storage']['hdd_size'] is not None:
            query_string += "&A=" + specs['storage']['hdd_size'] + "000000000"

        url_with_query = "https://pcpartpicker.com/products/internal-hard-drive/#sort=price&R=4,5" + query_string
        if locate_product_and_click('HDD', url_with_query, browser):
            exact_specs_found['hdd'] = True
            wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")
    else:
        # HDD was not found on original PC
        exact_specs_found['hdd'] = True

    # Add CPU Cooling
    query_string = ""
    match specs['processor']['cooling']:
        # AIO
        case "Liquid":
            query_string += "&W=10120,10140,10240,10280,10360,10420"
        # Fan
        case "Air" | _:
            query_string += "&W=0"
   
    url_with_query = "https://pcpartpicker.com/products/cpu-cooler/#sort=price&R=4,5" + query_string
    if locate_product_and_click("Cooling", url_with_query, browser):
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
    estimated_wattage = ''
    if browser.current_url == "https://pcpartpicker.com/list":
        element = browser.find_element(By.CLASS_NAME, "partlist__keyMetric")
        estimated_wattage = element.text.replace("Estimated Wattage: ", "")[:-1]

    query_string = ""
    true_wattage = False

    # Found true wattage from parsed data
    if specs['power']['wattage'] is not None:
        true_wattage = True
        query_string = "&A=" + specs['power']['wattage'] + "000000000,2000000000000"
    
    # Using estimated wattage, could not match exact spec
    if estimated_wattage is not None and not true_wattage:
        exact_specs_found['psu'] = False
        query_string = "&A" + estimated_wattage + "000000000,2000000000000"

    url_with_query = "https://pcpartpicker.com/products/power-supply/#sort=price&R=4,5" + query_string
    if locate_product_and_click("PSU", url_with_query, browser):
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
    """
    Prints a message to the console based on user preferences and input parameters,
    comparing an original price with a new price and displaying information about
    potential savings or differences.

    Args:
        original_price (float | int): Required, representing the original price
            of a PC or product from an online store or website. Its value is used
            to calculate differences with new prices.
        new_price (float): Not calculated within the function, its purpose is to
            display the total cost so far after potentially making changes.
        url (str): Passed as an argument to the function, likely representing the
            URL where users can customize their PC build or explore more options.
        found_exact (bool): Used to determine whether the exact matching specs for
            the PC build have been found or not. Its value is likely set based on
            a prior comparison between desired and actual PC specifications.

    """
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
    """
    Initializes and returns a Chrome driver instance with specified options,
    including proxy settings, user agent, and browser configuration. The instance
    is created using either the Linux or standard version of the driver based on
    the operating system.

    Returns:
        Chrome: A browser driver instance with specified options and settings
        applied for use in web scraping or automation tasks, customized according
        to the operating system.

    """
    prox = PROXY_HOST + ":" + PROXY_PORT
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.140 Safari/537.36"
    chrome_options = uc.options.ChromeOptions()

    proxy_extension_path = './script/proxy_ext'
    chrome_options.add_argument("--load-extension=" + proxy_extension_path)
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("user-agent={}".format(user_agent))
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument(f"--proxy-server={prox}")

    return uc.Chrome(options=chrome_options, driver_executable_path="./script/drivers/chromedriver-linux64/chromedriver", version_main=126) if linux else uc.Chrome(options=chrome_options)

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
