# PClone
PClone is a quick, easy to use, script that enables the user to duplicate a gaming desktop into a PCPartPicker URL.

### Prerequisites
Make sure you have installed all of the following prerequisites on your machine:
* Requests - ```pip install requests```
* Selenium - ```pip install selenium```
* Undetected Chromedriver - ```pip install undetected-chromedriver```
* dotenv - ```pip install python-dotenv```

### Proxy
Make sure to use a proxy so PCPartPicker doesn't block you!

PROXY_HOST and PROXY_PORT is set in your .env file

```PROXY_HOST=123.43.23.1```

```PROXY_PORT=8080```

### PcPartPicker Mapping
In order to properly map parsed products to pcpartpicker, the files in the pcpartpicker folder need to be populated with their proper values. This allows the program to know how to build a URL query request. 

It is constantly updated as PcPartPicker adds new products to select on the site.

### How it works
  - First, given a valid URL, it parses the specifications of the desktop into a dictionary.
  - Then, it automates the process of building a PC on PCPartPicker by utilizing a headless Selenium Webdriver.
  - Finally, when the parts are all added, it outputs information on pricing, as well as the URL for further customization.

### Supported Sites
* BestBuy

### Future Plans
* Optimize
* Modularize
* Add support for Newegg links.
* Host on a server for public use
* Store parsed data from cached URLs
* More!

Example
```sh
> python main.py https://www.bestbuy.com/site/hp-omen-25l-gaming-desktop-intel-core-i7-14700f-32gb-ddr5-memory-nvidia-geforce-rtx-4060-ti-2tb-ssd-snow-white/6573317.p?skuId=6573317
```

Updates:
- 07/05/24: Refactor code, add proxies, move away from geckodriver to use undetected chromedriver
