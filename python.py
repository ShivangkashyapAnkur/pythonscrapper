from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import time
import os

# Initialize WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-extensions")
driver = webdriver.Chrome(options=options)

# URLs
login_url = "https://www.amazon.in/ap/signin"
categories_urls = [
    "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
    "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
    "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
    "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0"
    # Add more categories as needed
]

# Authentication
def login_amazon(username, password):
    driver.get(login_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_email"))).send_keys(username)
    driver.find_element(By.ID, "continue").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_password"))).send_keys(password)
    driver.find_element(By.ID, "signInSubmit").click()
    time.sleep(2)  # Wait for login to complete

# Scraping data from a single category
def scrape_category(category_url, category_name):
    driver.get(category_url)
    time.sleep(2)
    
    products = []
    for _ in range(3):  # Scroll to load more products (adjust based on site behavior)
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(2)
    
    items = driver.find_elements(By.CSS_SELECTOR, ".zg-grid-general-faceout")
    for item in items:
        try:
            product_name = item.find_element(By.CSS_SELECTOR, ".p13n-sc-truncate").text
            product_price = item.find_element(By.CSS_SELECTOR, ".p13n-sc-price").text
            discount = item.find_element(By.CSS_SELECTOR, ".a-size-small.a-color-price").text
            rating = item.find_element(By.CSS_SELECTOR, ".a-icon-alt").get_attribute("innerText")
            sold_by = item.find_element(By.CSS_SELECTOR, ".a-size-small.a-color-secondary").text
            images = [img.get_attribute("src") for img in item.find_elements(By.CSS_SELECTOR, "img")]
            
            # Filtering by discount (e.g., greater than 50%)
            if "50%" in discount:
                products.append({
                    "Category": category_name,
                    "Product Name": product_name,
                    "Product Price": product_price,
                    "Discount": discount,
                    "Rating": rating,
                    "Sold By": sold_by,
                    "Images": images
                })
        except NoSuchElementException:
            continue

    return products

# Main scraping function
def main(username, password):
    try:
        # Log in
        login_amazon(username, password)
        
        all_products = []
        for url in categories_urls:
            category_name = url.split("/")[-2].capitalize()  # Extract category name from URL
            print(f"Scraping category: {category_name}")
            category_products = scrape_category(url, category_name)
            all_products.extend(category_products)
        
        # Save data to a file
        with open("amazon_best_sellers.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["Category", "Product Name", "Product Price", "Discount", "Rating", "Sold By", "Images"])
            writer.writeheader()
            writer.writerows(all_products)
        
        print("Scraping completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

# Run the scraper
if __name__ == "__main__":
    USERNAME = os.getenv("AMAZON_USERNAME")  # Replace with your Amazon username or set in environment variables
    PASSWORD = os.getenv("AMAZON_PASSWORD")  # Replace with your Amazon password or set in environment variables
    main(USERNAME, PASSWORD)
