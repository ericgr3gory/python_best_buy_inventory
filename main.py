from playwright.sync_api import sync_playwright ,TimeoutError
from time import sleep
import os
from dotenv import load_dotenv
import requests
import logging

logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s [%(levelname)s] %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S',  # Date format
    handlers=[
        logging.StreamHandler(),  # Output logs to the console
        logging.FileHandler("script.log", mode='w')  # Output logs to a file (overwrites each run)
    ]
)

load_dotenv()


LINK = os.getenv('BEST_BUY_LINK')
#LINK_5000 = os.getenv('BEST_BUY_LINK_5000')
#LINK = os.getenv('BEST_BUY_LINK_TEST')
#LINK = os.getenv('BEST_BUY_giga_5090')

def start_playwright():
    return sync_playwright().start() 


def open_browser(pw):
    
    browser = pw.chromium.launch(headless=False,  # Run headless mode
        args=["--use-fake-ui-for-media-stream"]  # Force geolocation permission
        )
    context = browser.new_context(
        #geolocation={"latitude": 36.1699, "longitude": -115.1398},  # Las Vegas
        #geolocation={"latitude": 36.2553, "longitude": -115.6350},  # Mount Charleston
        geolocation={"latitude": 36.2826, "longitude": -115.2914},  # Centennial Hills
        permissions=["geolocation"],
        viewport={"width": 1920, "height": 1080}
        )
        
    logging.info('Browser with context created')
    page = context.new_page()
    logging.info('page created')    
    return browser, context, page
    
def load_page(browser, context, page):
    
    
    attempts = 0
    max_attenpts = 10
    while True:
        attempts += 1
        logging.info(f'{attempts} attempts to Load Page to Browser')
        
        try:
            page.goto(LINK)
            logging.info('page loaded')
            return page
        
        except TimeoutError as e:
            logging.error(e)
            if attempts > max_attenpts:
                context.browser.close()
                quit("page won't Load")
            
        

def send_notification(title, message):
    API_TOKEN = os.getenv('API_TOKEN')
    USER_KEY = os.getenv('USER_KEY')
    
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": API_TOKEN,
        "user": USER_KEY,
        "title": title,
        "message": message
    }
    requests.post(url, data=data)
    
def check_button_state(page, sku):
    while True:
        
        try:
            button = page.locator(f"[data-sku-id='{sku}']")
            button = button.is_disabled()
            logging.info(f"button is disabled {button}")
            button_status = page.locator('[data-button-state="SOLD_OUT"]').count() > 0
            logging.info(f"button status sold out: {button_status}")
            return button and button_status
            
        except TimeoutError as e:
            logging.error(e)
            reloading_page(page)

def reloading_page(page):
    while True:
        try:
            logging.info('trying to reload') 
            page.reload()
            logging.info('page reloaded')
            return page
        
        except TimeoutError:
            logging.info('page failed to reload timeout')
            sleep(1)

def main():
    pw = start_playwright()
    browser, context, page = open_browser(pw)
    page = load_page(browser, context, page)
    
    sku = (LINK[-7:])
        
    button_status_is_soldout = check_button_state(page, sku)
        
    while button_status_is_soldout:
        button_status_is_soldout = check_button_state(page, sku)
        reloading_page(page)
                
    button = page.locator(f"[data-sku-id='{sku}']")    
    button_status = page.locator('data-button-state="ADD_TO_CART"')
    logging.info(button)
    logging.info(button_status)
    if (button.is_enabled() and button_status):
        logging.info('run to the store')
        send_notification("BUY", LINK)
            
if __name__ == '__main__':
        
    
    main()