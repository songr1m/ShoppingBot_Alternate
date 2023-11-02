from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from datetime import datetime
import requests

def click_add_to_cart(driver):
    add_to_cart_btn = None

    while not add_to_cart_btn:
        try:
            add_to_cart_btn = driver.find_element(By.XPATH, '//*[@id="add-to-cart-form:add-to-cart-section"]/div/div/div/div[2]/a')
        except:
            OrderStatus = driver.find_element(By.XPATH, '//*[@id="add-to-cart-form:add-to-cart-section"]/div/div/button/span').text
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{current_time} - Button not clickable yet - Order Status: {OrderStatus}, waiting and try again...")
            time.sleep(3)
            driver.refresh()
    add_to_cart_btn.click()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{current_time} - add_to_cart_btn clicked")
    time.sleep(5)


def BotSetup(item_url, max_price, options):
    service_object = Service("c:\webdrivers\chromedriver.exe")
    driver = webdriver.Chrome(options=options, service=service_object)
    driver.get(item_url)
    driver.maximize_window()
    click_add_to_cart(driver)


# Define preselected URLs and Maximalprices
preselected_urls_and_max_prices = [
    # Placeholder values for preselected URLs and max prices
    # nvidia
    #("https://www.alternate.de/Outlet/Grafikkarten/NVIDIA-Grafikkarten/RTX-4090", 1400.00),
    #("https://www.alternate.de/Outlet/Grafikkarten/NVIDIA-Grafikkarten/RTX-4080", 1000.00),
    #("https://www.alternate.de/Outlet/Grafikkarten/NVIDIA-Grafikkarten/RTX-4070-TI", 600.00),
    #("https://www.alternate.de/Outlet/Grafikkarten/NVIDIA-Grafikkarten/RTX-4070", 450.00),
    ("https://www.alternate.de/Outlet/Grafikkarten/NVIDIA-Grafikkarten/GeForce-RTX-Gaming?t=-21466&pr1=297&pr2=500&s=newest", 500.00),
    # AMD
    ("https://www.alternate.de/Outlet/Grafikkarten/AMD-Grafikkarten", 500.00),
    # CPU
    ("https://www.alternate.de/Outlet/CPUs", 150.00),
]

# Ask the user for input
print("Aktuelle Preselection der URLs und MaxPrices")
for url, price in preselected_urls_and_max_prices:
    print(url, price)

RefreshIntervallByUser = float(input("Please define the refresh interval in seconds: "))
user_input = input("Choose an option:\n1. Enter URLs and Maximalprices manually\n2. Use preselected URLs and Maximalprices\n")

if user_input == "1":
    # Get input from the user
    urls_and_max_prices = []
    while True:
        url = input("Enter the URL to monitor (or button e to exit & start running the script): ")
        if url == "e":
            break
        max_price = float(input("Enter the maximum price to monitor for this URL: "))
        urls_and_max_prices.append((url, max_price))
else:
    # Use preselected URLs and Maximalprices
    urls_and_max_prices = preselected_urls_and_max_prices

# Start the WebDriver and load each page
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

drivers = []
for url, _ in urls_and_max_prices:
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.maximize_window()
    drivers.append(driver)

visited_urls = set()

def refresh_url(driver, url):
    while True:
        time.sleep(RefreshIntervallByUser)
        driver.refresh()
        refreshed_url = driver.current_url
        response = requests.get(refreshed_url)
        status_code = response.status_code
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time} - Refreshed URL: {refreshed_url} - Status Code: {status_code}")

# Start separate threads for refreshing URLs
for i, driver in enumerate(drivers):
    url, _ = urls_and_max_prices[i]
    Thread(target=refresh_url, args=(driver, url)).start()

while True:
    for i, driver in enumerate(drivers):
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        url, max_price = urls_and_max_prices[i]
        response = requests.get(url)

        if response.status_code == 200:
            itemlist = soup.find_all("a", class_="card align-content-center productBox boxCounter text-font")

            for item in itemlist:
                price = item.find("span", class_="price").text.strip()
                price_float = float(price.split()[1].replace('.', '').replace(',', '.'))
                item_url = item['href']

                if price_float < max_price and item_url not in visited_urls:
                    visited_urls.add(item_url)
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"{current_time} - Item found below max price: {item_url}")

                    Thread(target=BotSetup, args=(item_url, max_price, options)).start()

    time.sleep(1)

 # Ausgabe der besuchten URLs
    print("Visited URLs:")
    for visited_url in visited_urls:
        print(visited_url)