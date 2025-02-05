from playwright.sync_api import sync_playwright ,TimeoutError
from time import sleep
import os
from dotenv import load_dotenv
import requests
import logging
import vpn

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
    max_attempts = 10
    while True:
        attempts += 1
        logging.info(f'{attempts} attempts to Load Page to Browser')
        
        try:
            page.goto(LINK)
            logging.info('page loaded')
            return page
        
        except TimeoutError as e:
            logging.error(e)
            logging.info('stopping vpn')
            vpn.stop_openvpn()
            logging.info('starting vpn')
            vpn.start_openvpn()
            sleep(5)
            if attempts > max_attempts:
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
    
def check_button_state(page, sku, state):
        
    try:
        button = page.locator(f"[data-sku-id='{sku}']")
        button = button.is_disabled()
        logging.info(f"button is disabled {button}")
        button_status = page.locator(f'[data-button-state="{state}"]').count() > 0
        logging.info(f"button status sold out: {button_status}")
        return button and button_status
            
    except TimeoutError as e:
        logging.error(e)
        return True

def reloading_page(page):
    attempts = 0
    max_attempts = 5
    while True:
        attempts += 1
        try:
            logging.info('trying to reload') 
            page.reload()
            logging.info('page reloaded')
            return page
        
        except TimeoutError as e:
            logging.info(f'{e}page failed to reload timeout')
            logging.info('stopping vpn')
            vpn.stop_openvpn()
            logging.info('starting vpn')
            vpn.start_openvpn()
            sleep(5)
            if attempts > max_attempts:
                logging.info('max atempts reached exiting')
                quit()

def main():
    pw = start_playwright()
    browser, context, page = open_browser(pw)
    page = load_page(browser, context, page)
    sku = (LINK[-7:])
        
    button_status_is_soldout = check_button_state(page, sku, 'SOLD_OUT')
        
    while button_status_is_soldout:
        reloading_page(page)
        button_status_is_soldout = check_button_state(page, sku, 'SOLD_OUT')
    
    button_status_is_add_cart = check_button_state(page, sku, 'ADD_TO_CART')
    
    if button_status_is_add_cart:
        logging.info('run to the store')
        send_notification("BUY", LINK)
            
if __name__ == '__main__':
        
    
    main()