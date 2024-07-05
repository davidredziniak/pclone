import json
import re
import requests
import os
import sys
import undetected_chromedriver as uc
from timeit import default_timer as timer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium_stealth import stealth

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

mobo_map = {'DDR2': '2', 'DDR3': '3', 'DDR4': '4', 'DDR5': '5'}

gpu_map = {
  "Arc A310": "562",
  "Arc A380": "538",
  "Arc A580": "561",
  "Arc A750": "541",
  "Arc A770": "540",
  "Arc Pro A40": "576",
  "Arc Pro A50": "578",
  "Arc Pro A60": "577",
  "FireGL V7300": "107",
  "FirePro 2270": "193",
  "FirePro 2450": "86",
  "FirePro 2460": "94",
  "FirePro R5000": "197",
  "FirePro RG220A": "203",
  "FirePro S7000": "198",
  "FirePro S9000": "205",
  "FirePro S9050": "200",
  "FirePro S9150": "201",
  "FirePro S10000": "206",
  "FirePro V3800": "133",
  "FirePro V3900": "90",
  "FirePro V4900": "92",
  "FirePro V5700": "111",
  "FirePro V5800": "88",
  "FirePro V5900": "98",
  "FirePro V7750": "125",
  "FirePro V7900": "93",
  "FirePro V7900 SDI": "195",
  "FirePro V8750": "128",
  "FirePro V8800": "129",
  "FirePro V9800": "108",
  "FirePro W600": "192",
  "FirePro W2100": "191",
  "FirePro W4100": "190",
  "FirePro W4300": "364",
  "FirePro W5000": "140",
  "FirePro W5100": "188",
  "FirePro W7000": "196",
  "FirePro W7100": "207",
  "FirePro W8000": "194",
  "FirePro W8100": "189",
  "FirePro W9000": "199",
  "FirePro W9100": "202",
  "GeForce 210": "1",
  "GeForce 7200 GS": "32",
  "GeForce 8400 GS": "31",
  "GeForce 8500 GT": "36",
  "GeForce 9400 GT": "23",
  "GeForce 9500 GT": "34",
  "GeForce 9600 GSO": "22",
  "GeForce 9600 GT": "361",
  "GeForce 9800 GT": "30",
  "GeForce 9800 GTX+": "24",
  "GeForce FX 5200": "35",
  "GeForce GT 220": "2",
  "GeForce GT 430": "48",
  "GeForce GT 440": "49",
  "GeForce GT 520": "54",
  "GeForce GT 610": "103",
  "GeForce GT 620": "104",
  "GeForce GT 630": "105",
  "GeForce GT 640": "106",
  "GeForce GT 710": "362",
  "GeForce GT 720": "183",
  "GeForce GT 730": "175",
  "GeForce GT 740": "174",
  "GeForce GT 1030": "396",
  "GeForce GT 1030 DDR4": "423",
  "GeForce GTS 250": "4",
  "GeForce GTS 450": "50",
  "GeForce GTX 260": "160",
  "GeForce GTX 275": "5",
  "GeForce GTX 285": "6",
  "GeForce GTX 295": "7",
  "GeForce GTX 460": "8",
  "GeForce GTX 460 SE": "46",
  "GeForce GTX 460 X2": "56",
  "GeForce GTX 465": "9",
  "GeForce GTX 470": "10",
  "GeForce GTX 480": "11",
  "GeForce GTX 550 Ti": "51",
  "GeForce GTX 560": "61",
  "GeForce GTX 560 SE": "102",
  "GeForce GTX 560 Ti": "47",
  "GeForce GTX 560 Ti 448": "69",
  "GeForce GTX 560 Ti X2": "66",
  "GeForce GTX 570": "39",
  "GeForce GTX 580": "40",
  "GeForce GTX 580 X2": "65",
  "GeForce GTX 590": "62",
  "GeForce GTX 650": "115",
  "GeForce GTX 650 Ti": "118",
  "GeForce GTX 650 Ti Boost": "132",
  "GeForce GTX 660": "114",
  "GeForce GTX 660 Ti": "113",
  "GeForce GTX 670": "101",
  "GeForce GTX 680": "83",
  "GeForce GTX 690": "100",
  "GeForce GTX 750": "163",
  "GeForce GTX 750 Ti": "164",
  "GeForce GTX 760": "142",
  "GeForce GTX 760 X2": "159",
  "GeForce GTX 770": "137",
  "GeForce GTX 780": "136",
  "GeForce GTX 780 Ti": "153",
  "GeForce GTX 950": "329",
  "GeForce GTX 950 75W": "366",
  "GeForce GTX 960": "208",
  "GeForce GTX 970": "186",
  "GeForce GTX 980": "185",
  "GeForce GTX 980 Ti": "224",
  "GeForce GTX 1050": "379",
  "GeForce GTX 1050 Ti": "380",
  "GeForce GTX 1060 3GB": "378",
  "GeForce GTX 1060 6GB": "373",
  "GeForce GTX 1070": "369",
  "GeForce GTX 1070 Ti": "415",
  "GeForce GTX 1080": "367",
  "GeForce GTX 1080 Ti": "390",
  "GeForce GTX 1630": "525",
  "GeForce GTX 1650 G5": "443",
  "GeForce GTX 1650 G6": "500",
  "GeForce GTX 1650 SUPER": "476",
  "GeForce GTX 1660": "439",
  "GeForce GTX 1660 SUPER": "450",
  "GeForce GTX 1660 Ti": "438",
  "GeForce GTX Titan": "130",
  "GeForce GTX Titan Black": "165",
  "GeForce GTX Titan X": "221",
  "GeForce GTX Titan Z": "173",
  "GeForce RTX 2060": "436",
  "GeForce RTX 2060 12GB": "514",
  "GeForce RTX 2060 SUPER": "446",
  "GeForce RTX 2070": "425",
  "GeForce RTX 2070 SUPER": "447",
  "GeForce RTX 2080": "427",
  "GeForce RTX 2080 SUPER": "448",
  "GeForce RTX 2080 Ti": "424",
  "GeForce RTX 3050 6GB": "572",
  "GeForce RTX 3050 8GB": "518",
  "GeForce RTX 3060 8GB": "546",
  "GeForce RTX 3060 12GB": "499",
  "GeForce RTX 3060 Ti": "497",
  "GeForce RTX 3060 Ti LHR": "513",
  "GeForce RTX 3070": "494",
  "GeForce RTX 3070 LHR": "508",
  "GeForce RTX 3070 Ti": "506",
  "GeForce RTX 3080 10GB": "492",
  "GeForce RTX 3080 10GB LHR": "507",
  "GeForce RTX 3080 12GB LHR": "516",
  "GeForce RTX 3080 Ti": "505",
  "GeForce RTX 3090": "493",
  "GeForce RTX 3090 Ti": "520",
  "GeForce RTX 4060": "552",
  "GeForce RTX 4060 Ti": "553",
  "GeForce RTX 4070": "550",
  "GeForce RTX 4070 SUPER": "565",
  "GeForce RTX 4070 Ti": "549",
  "GeForce RTX 4070 Ti SUPER": "566",
  "GeForce RTX 4080": "542",
  "GeForce RTX 4080 SUPER": "567",
  "GeForce RTX 4090": "539",
  "NVS 810": "410",
  "Quadro 400": "97",
  "Quadro 410": "210",
  "Quadro 2000D": "213",
  "Quadro 4000": "89",
  "Quadro 5000": "87",
  "Quadro 6000": "96",
  "Quadro FX 1800": "85",
  "Quadro GP100": "411",
  "Quadro GV100": "422",
  "Quadro K420": "218",
  "Quadro K600": "209",
  "Quadro K620": "220",
  "Quadro K1200": "222",
  "Quadro K2000": "177",
  "Quadro K2000D": "178",
  "Quadro K2200": "216",
  "Quadro K4000": "184",
  "Quadro K4000M": "212",
  "Quadro K4200": "217",
  "Quadro K5000": "211",
  "Quadro K5200": "219",
  "Quadro K6000": "155",
  "Quadro M2000": "374",
  "Quadro M4000": "352",
  "Quadro M5000": "358",
  "Quadro M6000": "223",
  "Quadro NVS 295": "215",
  "Quadro NVS 420": "91",
  "Quadro NVS 450": "95",
  "Quadro P400": "398",
  "Quadro P600": "399",
  "Quadro P620": "434",
  "Quadro P1000": "400",
  "Quadro P2000": "401",
  "Quadro P2200": "449",
  "Quadro P4000": "397",
  "Quadro P5000": "388",
  "Quadro P6000": "389",
  "Quadro RTX 4000": "440",
  "Quadro RTX 5000": "433",
  "Quadro RTX 6000": "432",
  "Quadro RTX 8000": "441",
  "Radeon 9550": "68",
  "Radeon HD 3450": "64",
  "Radeon HD 4350": "12",
  "Radeon HD 4550": "13",
  "Radeon HD 4650": "14",
  "Radeon HD 4670": "28",
  "Radeon HD 4670 X2": "45",
  "Radeon HD 4830": "44",
  "Radeon HD 4850": "25",
  "Radeon HD 4870": "29",
  "Radeon HD 4890": "67",
  "Radeon HD 5450": "26",
  "Radeon HD 5550": "27",
  "Radeon HD 5570": "33",
  "Radeon HD 5670": "15",
  "Radeon HD 5750": "16",
  "Radeon HD 5770": "17",
  "Radeon HD 5830": "18",
  "Radeon HD 5850": "19",
  "Radeon HD 5870": "20",
  "Radeon HD 5870 X2": "43",
  "Radeon HD 5970": "21",
  "Radeon HD 6450": "55",
  "Radeon HD 6570": "57",
  "Radeon HD 6670": "58",
  "Radeon HD 6750": "59",
  "Radeon HD 6770": "60",
  "Radeon HD 6790": "53",
  "Radeon HD 6850": "42",
  "Radeon HD 6870": "41",
  "Radeon HD 6870 X2": "63",
  "Radeon HD 6950": "37",
  "Radeon HD 6970": "38",
  "Radeon HD 6990": "52",
  "Radeon HD 7750": "80",
  "Radeon HD 7770": "79",
  "Radeon HD 7770 GHz Edition": "109",
  "Radeon HD 7790": "131",
  "Radeon HD 7850": "81",
  "Radeon HD 7870": "82",
  "Radeon HD 7870 GHz Edition": "110",
  "Radeon HD 7870 XT": "124",
  "Radeon HD 7950": "71",
  "Radeon HD 7970": "70",
  "Radeon HD 7970 GHz Edition": "112",
  "Radeon HD 7990": "122",
  "Radeon Pro Duo": "365",
  "Radeon Pro Duo Polaris": "408",
  "Radeon Pro VII": "487",
  "Radeon Pro W5500": "486",
  "Radeon Pro W5700": "479",
  "Radeon PRO W6400": "543",
  "Radeon PRO W6600": "544",
  "Radeon PRO W6800": "545",
  "Radeon PRO W7500": "563",
  "Radeon PRO W7600": "564",
  "Radeon PRO W7700": "573",
  "Radeon PRO W7800": "557",
  "Radeon PRO W7900": "556",
  "Radeon Pro WX 2100": "412",
  "Radeon Pro WX 3100": "413",
  "Radeon Pro WX 3200": "485",
  "Radeon Pro WX 4100": "385",
  "Radeon Pro WX 5100": "387",
  "Radeon Pro WX 7100": "386",
  "Radeon Pro WX 8200": "442",
  "Radeon Pro WX 9100": "414",
  "Radeon R5 220": "359",
  "Radeon R5 230": "179",
  "Radeon R7 240": "151",
  "Radeon R7 250": "150",
  "Radeon R7 250X": "161",
  "Radeon R7 260": "162",
  "Radeon R7 260X": "149",
  "Radeon R7 265": "168",
  "Radeon R7 350": "382",
  "Radeon R7 360": "308",
  "Radeon R7 370": "309",
  "Radeon R9 270": "154",
  "Radeon R9 270X": "147",
  "Radeon R9 280": "167",
  "Radeon R9 280X": "148",
  "Radeon R9 285": "182",
  "Radeon R9 290": "152",
  "Radeon R9 290X": "146",
  "Radeon R9 295X2": "169",
  "Radeon R9 380": "310",
  "Radeon R9 380X": "355",
  "Radeon R9 390": "311",
  "Radeon R9 390X": "312",
  "Radeon R9 390X2": "332",
  "Radeon R9 Fury": "326",
  "Radeon R9 Fury X": "319",
  "Radeon R9 Nano": "330",
  "Radeon RX 460": "377",
  "Radeon RX 470": "376",
  "Radeon RX 480": "370",
  "Radeon RX 550 - 512": "394",
  "Radeon RX 550 - 640": "420",
  "Radeon RX 560 - 896": "416",
  "Radeon RX 560 - 1024": "395",
  "Radeon RX 570": "392",
  "Radeon RX 580": "391",
  "Radeon RX 590": "431",
  "Radeon RX 5500 XT": "478",
  "Radeon RX 5600 XT": "484",
  "Radeon RX 5700": "445",
  "Radeon RX 5700 XT": "444",
  "Radeon RX 6400": "521",
  "Radeon RX 6500 XT": "517",
  "Radeon RX 6600": "511",
  "Radeon RX 6600 XT": "509",
  "Radeon RX 6650 XT": "522",
  "Radeon RX 6700": "526",
  "Radeon RX 6700 XT": "501",
  "Radeon RX 6750 XT": "523",
  "Radeon RX 6800": "495",
  "Radeon RX 6800 XT": "496",
  "Radeon RX 6900 XT": "498",
  "Radeon RX 6950 XT": "524",
  "Radeon RX 7600": "554",
  "Radeon RX 7600 XT": "571",
  "Radeon RX 7700 XT": "558",
  "Radeon RX 7800 XT": "559",
  "Radeon RX 7900 GRE": "560",
  "Radeon RX 7900 XT": "547",
  "Radeon RX 7900 XTX": "548",
  "Radeon RX VEGA 56": "404",
  "Radeon RX VEGA 64": "405",
  "Radeon VII": "437",
  "RTX 4000 SFF Ada Generation": "551",
  "RTX 6000 Ada Generation": "555",
  "RTX A400": "574",
  "RTX A1000": "575",
  "RTX A2000 6GB": "527",
  "RTX A2000 12GB": "528",
  "RTX A4000": "510",
  "RTX A4500": "529",
  "RTX A5000": "530",
  "RTX A5500": "531",
  "RTX A6000": "504",
  "T400 4GB": "536",
  "T400 2GB": "532",
  "T600": "533",
  "T1000 4GB": "534",
  "T1000 8GB": "535",
  "TITAN RTX": "435",
  "Titan V": "417",
  "Titan X (Pascal)": "375",
  "Titan Xp": "393",
  "Vega Frontier Edition": "402",
  "Vega Frontier Edition Liquid": "403"
}

mem_map = {'0': '', '1': '1024001,1024002', '2': '2048001,2048002', '3': '3072003',
           '4': '4096001,4096002', '6': '6144003', '8': '8192001,8192002,8192004',
           '16': '16384001,16384002,16384004,16384008', '24': '24576001,24576003,24576006',
           '32': '32768001,32768002,32768004,32768008', '48': '49152001,49152002,49152003',
           '64': '65536001,65536002,65536004,65536008', '128': '131072001,131072004,131072008', '256': '262144008'}

# Define required specifications for PcPartPicker
general = dict.fromkeys(['price', 'case_color', 'wifi'])
processor = dict.fromkeys(['brand', 'full_model_name', 'model', 'model_num', 'cooling'])
storage = dict.fromkeys(['type', 'hdd_size', 'hdd_rpm', 'ssd_size', 'ssd_interface'])
memory = dict.fromkeys(['type', 'size', 'clock', 'amount'])
graphics = dict.fromkeys(['model', 'amount', 'memory', 'cooling'])
power = dict.fromkeys(['wattage'])
expansion = dict.fromkeys(['pcie_x1', 'pcie_x4', 'pcie_x8', 'pcie_x16', 'internal2-5', 'internal3-5', 'external3-5', 'external5-25', 'm2_slots'])
specs = {'general': general, 'processor': processor, 'storage': storage, 'memory': memory, 'graphics': graphics, 'power': power,
             'expansion': expansion}
exact_specs_found = {'cpu': False, 'gpu': False, 'motherboard': False, 'memory': False, 'ssd': False, 'hdd': False, 'cooling': False, 'case': False, 'psu': False}

def retrieve_pc_specs(url):
    # Define
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    # Best Buy specific filtering
    cpu_filter = {'cpu': ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', '13th', '14th', 'Generation', '3000', '5000', '7000', '9000', 'Series']}
    gpu_map_fix = {'GeForce RTX 3080': {'': 'GeForce RTX 3080 10GB', '10': 'GeForce RTX 3080 10GB', '12': 'GeForce RTX 3080 12GB LHR'}, 
                    'GeForce RTX 3060': {'': 'GeForce RTX 3060 8GB', '8': 'GeForce RTX 3060 8GB', '12': 'GeForce RTX 3060 12GB'},
                    'GeForce RTX 3050': 'GeForce RTX 3050 6GB',
                    'GeForce GTX 1650': 'GeForce GTX 1650 G5'}
    
    # Send a GET request to the user provided URL
    res = requests.get(url, headers=headers, verify=True)

    # Retrieve Price of PC
    price = re.search(
        'data-testId="customer-price" tabindex="-1"><span aria-hidden="true">\$(.*?)</span>', res.text).group(1)
    price = float(price.replace(',', ''))
    specs['general']['price'] = price

    # Search for the specifications in JSON format
    json_string = re.search(
        '<script type="application/json" id="shop-specifications-[0-9]*-json">(.*?)</script>',
        res.text, re.IGNORECASE)
    j_obj = json.loads(json_string.group(1))

    f = open('Missing.txt', 'w')

    # Parse specifications from various categories
    for section in j_obj['specifications']['categories']:
        match section['displayName']:
            # Find Case Color
            case "General":
                for detail in section['specifications']:
                    match detail['displayName']:
                        case "Color Category":
                            specs['general']['case_color'] = detail['value']
                        case _:
                            f.write("General: %s - %s\n" % (detail['displayName'], detail['value']))
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
                        case _:
                            f.write("CPU: %s - %s\n" % (detail['displayName'], detail['value']))
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
                        case _:
                            f.write("Storage: %s - %s\n" % (detail['displayName'], detail['value']))
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
                        case _:
                            f.write("Memory: %s - %s\n" % (detail['displayName'], detail['value']))
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
                        case _:
                            f.write("Graphics: %s - %s\n" % (detail['displayName'], detail['value']))
            # Find if PC has WiFi
            case "Connectivity":
                for detail in section['specifications']:
                    if detail['displayName'] == "Wireless Connectivity":
                        if "Wi-Fi" in detail['value']:
                            specs['general']['wifi'] = True
                    else:
                        f.write("Connectivity: %s - %s\n" % (detail['displayName'], detail['value']))
            # Find CPU/GPU Cooler Type (Liquid/Air)
            case "Cooling":
                for detail in section['specifications']:
                    match detail['displayName']:
                        case "CPU Cooling System":
                            specs['processor']['cooling'] = detail['value']
                        case "GPU Cooling System":
                            specs['graphics']['cooling'] = detail['value']
                        case _:
                            f.write("Cooling: %s - %s\n" % (detail['displayName'], detail['value']))
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
                        case _:
                            f.write("Expansion: %s - %s\n" % (detail['displayName'], detail['value']))
    f.close()

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

    # Output parsed data (DEV)
    f = open("Parsed.txt", "w")
    f.write(json.dumps(specs))
    f.close()

    print("Successfully parsed PC specifications...")
    return specs

# Find a (specified) product and clicks button to add to the build
def locate_product_and_click(name, url, browser, product_name = None):
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
            print("added")
            return True
                
def wait_for_webpage(browser, timeout, type, element):
    try:
        WebDriverWait(browser, timeout).until(EC.presence_of_element_located((type, element)))
        return True
    except TimeoutException:
        print("Loading took too much time!")
        return False
    
def exit_program(browser, message=""):
    if message != "":
        print(message)
    browser.quit()
    
def process_specs(browser, specs):
    # Begin process by going to pcpartpicker build homepage
    browser.get("https://pcpartpicker.com/list")

    # Wait for page load (locates if footer exists in DOM)
    if not wait_for_webpage(browser, 15, By.CLASS_NAME, "footer__copyright"):
        exit_program(browser, "Webpage did not load. Exiting")

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
   
    url_with_query = "https://pcpartpicker.com/products/internal-hard-drive/#sort=price&R=4,5" + query_string
    if locate_product_and_click("Cooling", url_with_query, browser):
        exact_specs_found['cooling'] = True
        wait_for_webpage(browser, 15, By.XPATH, "//div[@class='partlist__keyMetric']")

    # Add Case
    added_case = False
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
        print("On home")
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
        "pp_partlist_edit\(\'([a-zA-Z0-9]*)\'\)", browser.page_source)

    found_exact = True
    if False in exact_specs_found.values():
        found_exact = False
        
    # Pass information to output to user
    output(float(specs['general']['price']), float(total),
           "https://pcpartpicker.com/list/" + result.group(1), found_exact)


def output(original_price, new_price, url, found_exact):
    if not found_exact:
        print("\nOriginal: $" + str(original_price))
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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Missing URL.')
        exit(0)

    URL = str(sys.argv[1])
    print('Your URL is: %s' % URL)
    start = timer()

    # Parse PC Specs from Bestbuy
    parsed = retrieve_pc_specs(URL)

    # Create web driver
    prox = "185.199.229.156:7492"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.140 Safari/537.36"
    chrome_options = uc.ChromeOptions()
    #chrome_options.add_argument('--headless=new')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("user-agent={}".format(user_agent))
    chrome_options.add_argument(f"--proxy-server={prox}")
    browser = uc.Chrome(options=chrome_options)
    stealth(browser,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True
    )
    
    # Process specifications into PcPartPicker
    process_specs(browser, parsed)
    end = timer()
    # Close Selenium Webdriver
    exit_program(browser)
    print('\nTime elapsed: %s seconds.' % str(round(end - start, 2)))
