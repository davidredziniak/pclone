# PCloner
PCloner is a quick, easy to use, script that enables the user to duplicate a gaming desktop into a PCPartPicker URL.

### Prerequisites
Make sure you have installed all of the following prerequisites on your machine:
* Requests - ```pip install requests```
* Selenium - ```pip install selenium```

### How it works
  - First, it parses the specifications of the desktop, given a valid URL, into a dictionary.
  - Then, it automates the process of building a PC on PCPartPicker by utilizing a headless Selenium Webdriver.
  - Finally, when the parts are all added, it spits out information on pricing, as well as the URL for further customization.

### Supported Sites
* BestBuy

### Future Plans
* Add support for Newegg links.
* Optimize

### Usage
Make sure geckodriver.exe is in the current working directory, and run the script from the command line.

Example
```sh
> main.py https://www.bestbuy.com/site/hp-omen-gaming-desktop-amd-ryzen-7-series-3700x-16gb-memory-nvidia-geforce-rtx-2060-1tb-hdd-256gb-ssd-black/6402514.p?skuId=6402514
```
