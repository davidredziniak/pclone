import json
import re
import requests
import os
import sys
from timeit import default_timer as timer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

case_map = {'Beige/Gray': '5', 'Black': '6', 'Black/Blue': '10', 'Black/Clear': '99', 'Black/Gold': '11',
            'Black/Gray': '12', 'Black/Green': '13', 'Black/Orange': '16', 'Black/Pink': '17', 'Black/Purple': '18',
            'Black/Red': '19', 'Black/Silver': '20', 'Black/White': '21', 'Black/Yellow': '22', 'Blue': '23',
            'Blue/Black': '24', 'Blue/Silver': '28', 'Brown': '30', 'Camo': '32', 'Clear': '33', 'Gold': '94',
            'Gray': '35', 'Gray/Black': '36', 'Gray/Silver': '38', 'Green': '40', 'Green/Black': '41',
            'Green/Blue': '42', 'Green/Silver': '43', 'Green/White': '44', 'Gunmetal': '45', 'Multicolor': '46',
            'Orange': '47', 'Orange/Black': '48', 'Orange/White': '49', 'Pink': '50', 'Pink/Black': '51',
            'Pink/Silver': '52', 'Red': '56', 'Red/Black': '58', 'Red/Blue': '59', 'Red/Silver': '60',
            'Red/White': '61', 'Silver': '62', 'Silver/Black': '64', 'Silver/Gray': '66', 'White': '82',
            'White/Black': '83', 'White/Blue': '84', 'White/Gold': '100', 'White/Pink': '86', 'White/Purple': '87',
            'White/Red': '88', 'White/Silver': '89', 'Yellow': '90'}
cpu_map = {'AMD A4': '22', 'AMD A6': '20', 'AMD A8': '21', 'AMD A10': '25', 'AMD A12': '67', 'AMD Athlon': '32',
           'AMD Athlon II': '34', 'AMD Athlon II X2': '1', 'AMD Athlon II X3': '4', 'AMD Athlon II X4': '6',
           'AMD Athlon X2': '30', 'AMD Athlon X4': '31', 'AMD E2-Series': '33', 'AMD E-Series': '19',
           'AMD FX': '23', 'AMD Opteron': '57', 'AMD Phenom II X2': '5', 'AMD Phenom II X3': '7',
           'AMD Phenom II X4': '2', 'AMD Phenom II X6': '8', 'AMD Ryzen 3': '62', 'AMD Ryzen 5': '60',
           'AMD Ryzen 7': '59', 'AMD Ryzen 9': '69', 'AMD Sempron': '17', 'AMD Sempron X2': '29',
           'AMD Threadripper': '63', 'Intel Atom': '18', 'Intel Celeron': '3', 'Intel Core 2 Duo': '10',
           'Intel Core 2 Extreme': '16', 'Intel Core 2 Quad': '15', 'Intel Core i3': '11', 'Intel Core i5': '12',
           'Intel Core i7': '13', 'Intel Core i7 Extreme': '14', 'Intel Core i9': '61', 'Intel Pentium': '9',
           'Intel Pentium Gold': '68', 'Intel Xeon E': '70', 'Intel Xeon E3': '26', 'Intel Xeon E5': '27'}
gpu_map = {'FireGL V7300': '107', 'FirePro 2270': '193', 'FirePro 2450': '86', 'FirePro 2460': '94',
           'FirePro R5000': '197', 'FirePro RG220A': '203', 'FirePro S7000': '198', 'FirePro S9000': '205',
           'FirePro S9050': '200', 'FirePro S9150': '201', 'FirePro S10000': '206', 'FirePro V3800': '133',
           'FirePro V3900': '90', 'FirePro V4900': '92', 'FirePro V5700': '111', 'FirePro V5800': '88',
           'FirePro V5900': '98', 'FirePro V7750': '125', 'FirePro V7900': '93', 'FirePro V7900 SDI': '195',
           'FirePro V8750': '128', 'FirePro V8800': '129', 'FirePro V9800': '108', 'FirePro W600': '192',
           'FirePro W2100': '191', 'FirePro W4100': '190', 'FirePro W4300': '364', 'FirePro W5000': '140',
           'FirePro W5100': '188', 'FirePro W7000': '196', 'FirePro W7100': '207', 'FirePro W8000': '194',
           'FirePro W8100': '189', 'FirePro W9000': '199', 'FirePro W9100': '202', 'GeForce 210': '1',
           'GeForce 7200 GS': '32', 'GeForce 8400 GS': '31', 'GeForce 8500 GT': '36', 'GeForce 9400 GT': '23',
           'GeForce 9500 GT': '34', 'GeForce 9600 GSO': '22', 'GeForce 9600 GT': '361', 'GeForce 9800 GT': '30',
           'GeForce 9800 GTX+': '24', 'GeForce FX 5200': '35', 'GeForce GT 220': '2', 'GeForce GT 430': '48',
           'GeForce GT 440': '49', 'GeForce GT 520': '54', 'GeForce GT 610': '103', 'GeForce GT 620': '104',
           'GeForce GT 630': '105', 'GeForce GT 640': '106', 'GeForce GT 710': '362', 'GeForce GT 720': '183',
           'GeForce GT 730': '175', 'GeForce GT 740': '174', 'GeForce GT 1030': '396',
           'GeForce GT 1030 DDR4': '423', 'GeForce GTS 250': '4', 'GeForce GTS 450': '50',
           'GeForce GTX 260': '160',
           'GeForce GTX 275': '5', 'GeForce GTX 285': '6', 'GeForce GTX 295': '7', 'GeForce GTX 460': '8',
           'GeForce GTX 460 SE': '46', 'GeForce GTX 460 X2': '56', 'GeForce GTX 465': '9',
           'GeForce GTX 470': '10',
           'GeForce GTX 480': '11', 'GeForce GTX 550 Ti': '51', 'GeForce GTX 560': '61',
           'GeForce GTX 560 SE': '102', 'GeForce GTX 560 Ti': '47', 'GeForce GTX 560 Ti 448': '69',
           'GeForce GTX 560 Ti X2': '66', 'GeForce GTX 570': '39', 'GeForce GTX 580': '40',
           'GeForce GTX 580 X2': '65', 'GeForce GTX 590': '62', 'GeForce GTX 650': '115',
           'GeForce GTX 650 Ti': '118', 'GeForce GTX 650 Ti Boost': '132', 'GeForce GTX 660': '114',
           'GeForce GTX 660 Ti': '113', 'GeForce GTX 670': '101', 'GeForce GTX 680': '83',
           'GeForce GTX 690': '100',
           'GeForce GTX 750': '163', 'GeForce GTX 750 Ti': '164', 'GeForce GTX 760': '142',
           'GeForce GTX 760 X2': '159', 'GeForce GTX 770': '137', 'GeForce GTX 780': '136',
           'GeForce GTX 780 Ti': '153', 'GeForce GTX 950': '329', 'GeForce GTX 950 75W': '366',
           'GeForce GTX 960': '208', 'GeForce GTX 970': '186', 'GeForce GTX 980': '185',
           'GeForce GTX 980 Ti': '224', 'GeForce GTX 1050': '379', 'GeForce GTX 1050 Ti': '380',
           'GeForce GTX 1060 3GB': '378', 'GeForce GTX 1060 6GB': '373', 'GeForce GTX 1070': '369',
           'GeForce GTX 1070 Ti': '415', 'GeForce GTX 1080': '367', 'GeForce GTX 1080 Ti': '390',
           'GeForce GTX 1650': '443', 'GeForce GTX 1650 SUPER': '476', 'GeForce GTX 1660': '439',
           'GeForce GTX 1660 SUPER': '450', 'GeForce GTX 1660 Ti': '438', 'GeForce GTX Titan': '130',
           'GeForce GTX Titan Black': '165', 'GeForce GTX Titan X': '221', 'GeForce GTX Titan Z': '173',
           'GeForce RTX 2060': '436', 'GeForce RTX 2060 SUPER': '446', 'GeForce RTX 2070': '425',
           'GeForce RTX 2070 SUPER': '447', 'GeForce RTX 2080': '427', 'GeForce RTX 2080 SUPER': '448',
           'GeForce RTX 2080 Ti': '424', 'NVS 810': '410', 'Quadro 400': '97', 'Quadro 410': '210',
           'Quadro 2000D': '213', 'Quadro 4000': '89', 'Quadro 5000': '87', 'Quadro 6000': '96',
           'Quadro FX 1800': '85', 'Quadro GP100': '411', 'Quadro GV100': '422', 'Quadro K420': '218',
           'Quadro K600': '209', 'Quadro K620': '220', 'Quadro K1200': '222', 'Quadro K2000': '177',
           'Quadro K2000D': '178', 'Quadro K2200': '216', 'Quadro K4000': '184', 'Quadro K4000M': '212',
           'Quadro K4200': '217', 'Quadro K5000': '211', 'Quadro K5200': '219', 'Quadro K6000': '155',
           'Quadro M2000': '374', 'Quadro M4000': '352', 'Quadro M5000': '358', 'Quadro M6000': '223',
           'Quadro NVS 295': '215', 'Quadro NVS 420': '91', 'Quadro NVS 450': '95', 'Quadro P400': '398',
           'Quadro P600': '399', 'Quadro P620': '434', 'Quadro P1000': '400', 'Quadro P2000': '401',
           'Quadro P2200': '449', 'Quadro P4000': '397', 'Quadro P5000': '388', 'Quadro P6000': '389',
           'Quadro RTX 4000': '440', 'Quadro RTX 5000': '433', 'Quadro RTX 6000': '432',
           'Quadro RTX 8000': '441',
           'Radeon 9550': '68', 'Radeon HD 3450': '64', 'Radeon HD 4350': '12', 'Radeon HD 4550': '13',
           'Radeon HD 4650': '14', 'Radeon HD 4670': '28', 'Radeon HD 4670 X2': '45', 'Radeon HD 4830': '44',
           'Radeon HD 4850': '25', 'Radeon HD 4870': '29', 'Radeon HD 4890': '67', 'Radeon HD 5450': '26',
           'Radeon HD 5550': '27', 'Radeon HD 5570': '33', 'Radeon HD 5670': '15', 'Radeon HD 5750': '16',
           'Radeon HD 5770': '17', 'Radeon HD 5830': '18', 'Radeon HD 5850': '19', 'Radeon HD 5870': '20',
           'Radeon HD 5870 X2': '43', 'Radeon HD 5970': '21', 'Radeon HD 6450': '55', 'Radeon HD 6570': '57',
           'Radeon HD 6670': '58', 'Radeon HD 6750': '59', 'Radeon HD 6770': '60', 'Radeon HD 6790': '53',
           'Radeon HD 6850': '42', 'Radeon HD 6870': '41', 'Radeon HD 6870 X2': '63', 'Radeon HD 6950': '37',
           'Radeon HD 6970': '38', 'Radeon HD 6990': '52', 'Radeon HD 7750': '80', 'Radeon HD 7770': '79',
           'Radeon HD 7770 GHz Edition': '109', 'Radeon HD 7790': '131', 'Radeon HD 7850': '81',
           'Radeon HD 7870': '82', 'Radeon HD 7870 GHz Edition': '110', 'Radeon HD 7870 XT': '124',
           'Radeon HD 7950': '71', 'Radeon HD 7970': '70', 'Radeon HD 7970 GHz Edition': '112',
           'Radeon HD 7990': '122', 'Radeon Pro Duo': '365', 'Radeon Pro Duo Polaris': '408',
           'Radeon Pro VII': '487', 'Radeon Pro W5500': '486', 'Radeon Pro W5700': '479',
           'Radeon Pro WX 2100': '412', 'Radeon Pro WX 3100': '413', 'Radeon Pro WX 3200': '485',
           'Radeon Pro WX 4100': '385', 'Radeon Pro WX 5100': '387', 'Radeon Pro WX 7100': '386',
           'Radeon Pro WX 8200': '442', 'Radeon Pro WX 9100': '414', 'Radeon R5 220': '359',
           'Radeon R5 230': '179',
           'Radeon R7 240': '151', 'Radeon R7 250': '150', 'Radeon R7 250X': '161', 'Radeon R7 260': '162',
           'Radeon R7 260X': '149', 'Radeon R7 265': '168', 'Radeon R7 350': '382', 'Radeon R7 360': '308',
           'Radeon R7 370': '309', 'Radeon R9 270': '154', 'Radeon R9 270X': '147', 'Radeon R9 280': '167',
           'Radeon R9 280X': '148', 'Radeon R9 285': '182', 'Radeon R9 290': '152', 'Radeon R9 290X': '146',
           'Radeon R9 295X2': '169', 'Radeon R9 380': '310', 'Radeon R9 380X': '355', 'Radeon R9 390': '311',
           'Radeon R9 390X': '312', 'Radeon R9 390X2': '332', 'Radeon R9 Fury': '326',
           'Radeon R9 Fury X': '319',
           'Radeon R9 Nano': '330', 'Radeon RX 460': '377', 'Radeon RX 470': '376', 'Radeon RX 480': '370',
           'Radeon RX 550 - 512': '394', 'Radeon RX 550 - 640': '420', 'Radeon RX 560 - 896': '416',
           'Radeon RX 560 - 1024': '395', 'Radeon RX 570': '392', 'Radeon RX 580': '391',
           'Radeon RX 590': '431',
           'Radeon RX 5500 XT': '478', 'Radeon RX 5600 XT': '484', 'Radeon RX 5700': '445',
           'Radeon RX 5700 XT': '444', 'Radeon RX VEGA 56': '404', 'Radeon RX VEGA 64': '405',
           'Radeon VII': '437',
           'TITAN RTX': '435', 'Titan V': '417', 'Titan X (Pascal)': '375', 'Titan Xp': '393',
           'Vega Frontier Edition': '402', 'Vega Frontier Edition Liquid': '403'}
mem_map = {0: '', 1: '1024001,1024002', 2: '2048001,2048002', 3: '3072003',
           4: '4096001,4096002', 6: '6144003', 8: '8192001,8192002,8192004',
           16: '16384001,16384002,16384004', 24: '24576003,24576006',
           32: '32768001,32768002,32768004,32768008', 48: '49152003',
           64: '65536001,65536002,65536004,65536008', 128: '131072001,131072004,131072008', 256: '262144008'}
apu = ['Radeon RX Vega 11']


def retrieve_pc_specs(url):
    # Define
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    general = dict.fromkeys(['price', 'case_color', 'cpu_cooling', 'gpu_cooling', 'wifi'])
    processor = dict.fromkeys(['model', 'model_num', 'clock'])
    storage = dict.fromkeys(['hdd_size', 'hdd_rpm', 'ssd_size', 'ssd_interface'])
    memory = dict.fromkeys(['type', 'size', 'clock', 'amount'])
    graphics = dict.fromkeys(['model', 'amount', 'memory'])
    expansion = dict.fromkeys(
        ['pcie_x1', 'pcie_x4', 'pcie_x8', 'pcie_x16', 'internal2-5', 'internal3-5', 'external3-5', 'external5-25', 'm2_slots'])
    specs = {'general': general, 'processor': processor, 'storage': storage, 'memory': memory, 'graphics': graphics,
             'expansion': expansion}

    data_filter = {'cpu': ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', 'Generation']}

    # Send a GET request to the user provided URL
    res = requests.get(url, headers=headers, verify=True)
    # Retrieve Price of PC
    specs['general']['price'] = re.search('data-testId="customer-price" tabindex="-1"><span aria-hidden="true">\$(.*?)</span>', res.text).group(1)
    print(specs['general']['price'])
    json_string = re.search(
        '<script type="application/json" id="shop-specifications-[0-9]*-json">(.*?)</script>',
        res.text, re.IGNORECASE)
    j_obj = json.loads(json_string.group(1))

    f = open('Missing.txt', 'w')

    # Parse specifications from various categories
    for section in j_obj['specifications']['categories']:
        # Retrieve Case Color
        if section['displayName'] == 'General':
            for detail in section['specifications']:
                match detail['displayName']:
                    case 'Color':
                        specs['general']['case_color'] = detail['value']
                    case _:
                        f.write("General: " + detail['displayName'] + " - " + detail['value'] + "\n")
        # Retrieve Cooling
        if section['displayName'] == 'Cooling':
            for detail in section['specifications']:
                match detail['displayName']:
                    case 'CPU Cooling System':
                        specs['general']['cpu_cooling'] = detail['value']
                    case 'GPU Cooling System':
                        specs['general']['gpu_cooling'] = detail['value']
                    case _:
                        f.write("Cooling: " + detail['displayName'] + " - " + detail['value'] + "\n")
        # Retrieve Storage
        if section['displayName'] == 'Storage':
            for detail in section['specifications']:
                match detail['displayName']:
                    case 'Hard Drive Capacity':
                        specs['storage']['hdd_size'] = detail['value'].split(' ')[0]
                    case 'Hard Drive RPM':
                        specs['storage']['hdd_rpm'] = detail['value'].split(' ')[0]
                    case 'Solid State Drive Capacity':
                        specs['storage']['ssd_size'] = detail['value'].split(' ')[0]
                    case 'Solid State Drive Interface':
                        specs['storage']['ssd_interface'] = detail['value']
                    case _:
                        f.write("Storage: " + detail['displayName'] + " - " + detail['value'] + "\n")
        # Retrieve Memory
        if section['displayName'] == 'Memory':
            for detail in section['specifications']:
                match detail['displayName']:
                    case 'System Memory (RAM)':
                        specs['memory']['size'] = int(detail['value'].split(' ')[0])
                    case 'System Memory RAM Speed':
                        specs['memory']['clock'] = detail['value'].split(' ')[0]
                    case 'Type of Memory (RAM)':
                        specs['memory']['type'] = detail['value'].split(' ')[0]
                    case 'Number of Memory Sticks Included':
                        specs['memory']['amount'] = int(detail['value'])
                    case _:
                        f.write("Memory: " + detail['displayName'] + " - " + detail['value'] + "\n")
        # Retrieve GPU
        if section['displayName'] == 'Graphics':
            for detail in section['specifications']:
                if detail['displayName'] == 'Graphics':
                    match detail['displayName']:
                        case 'Graphics':
                            # Check if it is dual graphics cards
                            if 'Dual' in detail['value']:
                                specs['graphics']['model'] = detail['value'].split(' ', 2)[2]
                                specs['graphics']['amount'] = 2
                            else:
                                specs['graphics']['model'] = detail['value'].split(' ', 1)[1]
                                specs['graphics']['amount'] = 1
                        case 'GPU Video Memory (RAM)':
                            specs['graphics']['memory'] = int(round(float(detail['value'].split(' ')[0]) / 1024))
                        case _:
                            f.write("Graphics: " + detail['displayName'] + " - " + detail['value'] + "\n")
        # Retrieve CPU
        if section['displayName'] == 'Processor':
            for detail in section['specifications']:
                match detail['displayName']:
                    case 'Processor Model':
                        specs['processor']['model'] = detail['value']
                    case 'Processor Model Number':
                        specs['processor']['model_num'] = detail['value']
                    case 'Processor Speed (Base)':
                        hz = detail['value'].split(' ')
                        if 'gigahertz' in hz:
                            specs['processor']['clock'] = str(int(float(hz[0]) * 10))
                        else:
                            print('ERROR while parsing Processor Speed')
                    case _:
                        f.write("CPU: " + detail['displayName'] + " - " + detail['value'] + "\n")
        # Retrieve Motherboard specifications
        if section['displayName'] == 'Expansion':
            for detail in section['specifications']:
                match detail['displayName']:
                    case 'Number Of PCI-E x1 Slots':
                        specs['expansion']['pcie_x1'] = detail['value']
                    case 'Number Of PCI-E x4 Slots':
                        specs['expansion']['pcie_x4'] = detail['value']
                    case 'Number Of PCI-E x8 Slots':
                        specs['expansion']['pcie_x8'] = detail['value']
                    case 'Number Of PCI-E x16 Slots':
                        specs['expansion']['pcie_x16'] = detail['value']
                    case 'Number Of Internal 2.5" Bays':
                        specs['expansion']['internal2-5'] = detail['value']
                    case 'Number Of Internal 3.5" Bays':
                        specs['expansion']['internal3-5'] = detail['value']
                    case 'Number Of External 3.5 Expansion Bays':
                        specs['expansion']['external3-5'] = detail['value']
                    case 'Number Of External 5.25 Expansion Bays':
                        specs['expansion']['external5-25'] = detail['value']
                    case 'Number of M.2 Slots':
                        specs['expansion']['m2_slots'] = int(detail['value'])
                    case _:
                        f.write("Expansion: " + detail['displayName'] + " - " + detail['value'] + "\n")
        # Retrieve Wifi
        if section['displayName'] == 'Connectivity':
            for detail in section['specifications']:
                if detail['displayName'] == 'Wireless Connectivity':
                    if "Wi-Fi" in detail['value']:
                        specs['general']['wifi'] = True

    f.close()
    f = open("Parsed.txt", "w")
    f.write(json.dumps(specs))
    f.close()
    print("Successfully parsed PC specifications...")
    return specs


def locate_product_and_click(name, browser):

    wait_for_webpage(browser, timeout=10)
    print('Locating %s...' % name, end='')
    products = browser.find_element_by_xpath("//table[@id='paginated_table']//tbody").find_elements_by_tag_name('tr')
    if len(products) == 0:
        print('ERROR')
        return False
    else:
        for product in products:
            price = product.find_element_by_class_name('td__price')
            if '$' in price.text:
                product.find_element_by_tag_name('button').click()
                print('added')
                return True


def wait_for_webpage(browser, timeout):
    WebDriverWait(browser, timeout).until(lambda d: d.execute_script("return jQuery.active == 0"))


def is_alert_present(browser):
    try:
        browser.switch_to.alert
        return True
    except:
        return False


def process_specs(specs):
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.headless = True
    browser = webdriver.Firefox(options=firefox_options, executable_path=r'' + os.getcwd() + '\geckodriver.exe')
    browser.get('https://pcpartpicker.com/list')

    if specs['processor']['clock'] is None:
        print("Clock for CPU is not available.")
        browser.close()
        exit(0)

    # Add CPU. Matches CPU model and base clock and picks listing with a price tag.
    browser.get(
        'https://pcpartpicker.com/products/cpu/#s=' + cpu_map[specs['processor']['model']] + '&A=' + specs['processor'][
            'clock'] + '00000000000')

    while is_alert_present(browser):
        browser.get(
            'https://pcpartpicker.com/products/cpu/#s=' + cpu_map[specs['processor']['model']] + '&A=' +
            specs['processor'][
                'clock'] + '00000000000')
        continue

    wait_for_webpage(browser, timeout=10)
    print('Locating CPU...', end='')
    products = browser.find_element_by_xpath("//table[@id='paginated_table']//tbody").find_elements_by_tag_name('tr')

    original_cpu_name = ''
    if 'Intel' in specs['processor']['model']:
        original_cpu_name = str.join(' ', specs['processor']['model'].split(' ')[:2]) + ' ' + specs['processor'][
            'model_num']
    else:
        original_cpu_name = specs['processor']['model'] + ' ' + specs['processor']['model_num']

    for product in products:
        name = product.find_element_by_tag_name('p').text
        price = product.find_element_by_class_name('td__price')
        if '$' in price.text and name == original_cpu_name:
            product.find_element_by_tag_name('button').click()
            print('added')
            break

    # Add GPU. Matches chipset and finds cheapest card.
    if specs['graphics']['model'] not in apu:
        browser.get(
            'https://pcpartpicker.com/products/video-card/#sort=price&c=' + gpu_map[specs['graphics']['model']])
        while is_alert_present(browser):
            browser.get(
                'https://pcpartpicker.com/products/video-card/#sort=price&c=' + gpu_map[specs['graphics']['model']])
            continue
        if not locate_product_and_click('Video Card', browser):
            browser.close()
            exit(0)

        # Add Additional GPU
        if specs['graphics']['amount'] == 2:
            if browser.current_url != 'https://pcpartpicker.com/list/': browser.get(
                'https://pcpartpicker.com/list/')
            button = browser.find_element_by_xpath(
                "//td[@class='td__addComponent']//a[@class='button  button--icon button--small pp_add_part_by_identifier']")
            button.click()

    # Add Motherboard
    mobo_map = {'DDR2': '2', 'DDR3': '3', 'DDR4': '4'}
    query_string = ''

    if specs['expansion']['pcie_x1'] is not None:
        query_string += ('&B=%s,6' % specs['expansion']['pcie_x1'])
    if specs['expansion']['pcie_x4'] is not None:
        query_string += ('&b=%s,3' % specs['expansion']['pcie_x4'])
    if specs['expansion']['pcie_x8'] is not None:
        query_string += ('&H=%s,6' % specs['expansion']['pcie_x8'])
    if specs['expansion']['pcie_x16'] is not None:
        query_string += ('&h=%s,8' % specs['expansion']['pcie_x16'])
    if specs['general']['wifi'] is True:
        query_string += '&V=8000,6001,6000,4000'

    browser.get('https://pcpartpicker.com/products/motherboard/#sort=price&L=%s' %(
            mobo_map[specs['memory']['type']] + query_string))
    while is_alert_present(browser):
        browser.get(
            'https://pcpartpicker.com/products/motherboard/#sort=price&L=%s' %(
            mobo_map[specs['memory']['type']] + query_string))
        continue
    if not locate_product_and_click('Motherboard', browser):
        browser.close()
        exit(0)

    # Add Memory
    query_string = ''
    if specs['memory']['clock'] is not None:
        query_string += '&S=' + specs['memory']['clock']
    browser.get('https://pcpartpicker.com/products/memory/#sort=price&R=4,5&Z=%s' % (
                mem_map[specs['memory']['size']] + query_string))
    while is_alert_present(browser):
        browser.get(
            'https://pcpartpicker.com/products/memory/#sort=price&R=4,5&Z=%s' % (
                    mem_map[specs['memory']['size']] + query_string))
        continue
    if not locate_product_and_click('Memory', browser):
        browser.close()
        exit(0)

    # Add SSD
    if specs['storage']['ssd_size'] is not None:
        browser.get('https://pcpartpicker.com/products/internal-hard-drive/#sort=price&R=4,5&t=0&A=%s000000000' %
                    specs['storage']['ssd_size'])
        while is_alert_present(browser):
            browser.get('https://pcpartpicker.com/products/internal-hard-drive/#sort=price&R=4,5&t=0&A=%s000000000' %
                        specs['storage']['ssd_size'])
            continue
        if not locate_product_and_click('SSD', browser):
            browser.close()
            exit(0)

    # Add HDD
    if specs['storage']['hdd_size'] is not None:
        browser.get('https://pcpartpicker.com/products/internal-hard-drive/#sort=price&R=4,5&t=%s&A=%s000000000' % (
        specs['storage']['hdd_rpm'], specs['storage']['hdd_size']))
        while is_alert_present(browser):
            browser.get('https://pcpartpicker.com/products/internal-hard-drive/#sort=price&R=4,5&t=%s&A=%s000000000' % (
                specs['storage']['hdd_rpm'], specs['storage']['hdd_size']))
            continue
        if not locate_product_and_click('HDD', browser):
            browser.close()
            exit(0)

    # Add Case
    added_case = False
    query_string = ''
    if specs['expansion']['internal2-5'] is not None:
        query_string += ('&K=' + specs['expansion']['internal2-5'] + ',17')
    if specs['expansion']['internal3-5'] is not None:
        query_string += ('&J=' + specs['expansion']['internal3-5'] + ',20')
    if specs['expansion']['external3-5'] is not None:
        query_string += ('&H=' + specs['expansion']['external3-5'] + ',15')
    if specs['expansion']['external5-25'] is not None:
        query_string += ('&G=' + specs['expansion']['external5-25'] + ',12')

    # Specs + Color matching case
    if specs['general']['case_color'] is not None and query_string != '':
        browser.get('https://pcpartpicker.com/products/case/#sort=price&c=%s%s' % (
            case_map[specs['general']['case_color']], query_string))
        while is_alert_present(browser):
            browser.get('https://pcpartpicker.com/products/case/#sort=price&c=%s%s' % (
                case_map[specs['general']['case_color']], query_string))
            continue
        if locate_product_and_click('Case (Color and specs matched)', browser=browser):
            added_case = True

    # Specs matching case
    if not added_case and query_string != '':
        browser.get('https://pcpartpicker.com/products/case/#sort=price&c=%s' %query_string)
        while is_alert_present(browser):
            browser.get('https://pcpartpicker.com/products/case/#sort=price&c=%s' %query_string)
            continue
        products = browser.find_elements_by_xpath("//tbody[@id='category_content']//tr")
        if locate_product_and_click('Case (Specs matched)', browser=browser):
            added_case = True

    # Color matching case
    if not added_case and specs['general']['case_color'] is not None:
        browser.get(
            'https://pcpartpicker.com/products/case/#sort=price&c=%s' % case_map[specs['general']['case_color']])
        while is_alert_present(browser):
            browser.get(
                'https://pcpartpicker.com/products/case/#sort=price&c=%s' % case_map[specs['general']['case_color']])
            continue
        if locate_product_and_click('Case (Color matched)', browser=browser):
            added_case = True

    # No case
    if not added_case:
        print('Could not find matching case..')

    # Add Power Supply
    element = browser.find_element_by_class_name('partlist__keyMetric')
    wattage = int(element.text.replace('Estimated Wattage: ', '')[:-1]) + 200
    browser.get(
        'https://pcpartpicker.com/products/power-supply/#sort=price&R=4,5&A=%s000000000,2000000000000' % str(wattage))
    while is_alert_present(browser):
        browser.get(
            'https://pcpartpicker.com/products/power-supply/#sort=price&R=4,5&A=%s000000000,2000000000000' % str(
                wattage))
        continue
    if not locate_product_and_click('Power Supply', browser=browser):
        browser.close()
        exit(0)

    # Retrieve new price
    if browser.current_url != 'https://pcpartpicker.com/list/': browser.get(
        'https://pcpartpicker.com/list/')
    WebDriverWait(browser, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//tr[@class='tr__total tr__total--final']")))

    total = float(
        browser.find_element_by_xpath("//tr[@class='tr__total tr__total--final']").text.replace('Total: ', '')[1:])
    result = re.search("pp_partlist_edit\(\'([a-zA-Z0-9]*)\'\)", browser.page_source)

    # Pass information to output to user
    output(original_price=float(specs['general']['price']), new_price=total,
           url='https://pcpartpicker.com/list/%s' % result.group(1))

    # Close Selenium Webdriver
    browser.close()


def output(original_price, new_price, url, notes=''):
    print('\nOriginal: $%s' % str(original_price))
    print('Your Total: $%s' % str(new_price))
    print('Difference: $%s' % str(round(abs(original_price - new_price), 2)))
    if original_price <= new_price or (original_price - new_price <= 100):
        print('You will likely not save any money building the PC yourself.')
    else:
        print('You can definitely save money building the PC yourself.')
    print('\nFeel free to customize:')
    print(url)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Missing URL.')
        exit(0)

    URL = str(sys.argv[1])
    print('Your URL is: %s' %URL)

    # BestBuy
    start = timer()
    s = retrieve_pc_specs(URL)
    #process_specs(s)
    end = timer()
    print('\nTime elapsed: %s seconds.' % str(round(end - start, 2)))
