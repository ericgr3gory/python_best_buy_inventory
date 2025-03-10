from playwright.sync_api import sync_playwright, TimeoutError
from playwright._impl._errors import Error
from time import sleep
import os
from dotenv import load_dotenv
import requests
import logging
import vpn
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/home/ericgr3gory/.local/logs/best_buy_scrape.log", mode='a')
    ]
)

load_dotenv()
LINK = os.getenv('BEST_BUY_LINK')

def handle_exception(exc_type, exc_value, exc_tb):
    logging.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))

sys.excepthook = handle_exception

PW = sync_playwright().start()

def open_browser(PW):
    browser = PW.chromium.launch(
        headless=False,
        args=["--use-fake-ui-for-media-stream"]
    )
    context = browser.new_context(
        geolocation={"latitude": 36.2826, "longitude": -115.2914},
        permissions=["geolocation"],
        viewport={"width": 1920, "height": 1080}
    )
    logging.info('Browser with context created')
    page = context.new_page()
    logging.info(f'Page created {LINK}')
    return browser, context, page

def load_page(browser, context, page, action):
    
    while True:
        
        try:
            if action == 'goto':
                logging.info(f'Trying to load{LINK}')
                page.goto(LINK)
                logging.info('Page loaded')
            if action == 'reload':
                logging.info(f'Trying to reload{LINK}')
                page.reload()
                logging.info('Page reloaded')
            return browser, context, page
        
        except (TimeoutError, Error) as e:
            
            if isinstance(e, TimeoutError) or "Page crashed" in str(e) or "Page.reload" in str(e):
                logging.info(f'{e} - page failed to reload')
                browser.close()
                return start_scraping_page()
            else:
                logging.error(f'{e}')
                send_notification('ERROR', e)
                browser.close()
                return start_scraping_page()
                

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
        disabled_state = page.locator(f"[data-sku-id='{sku}']").is_disabled()
        logging.info(f"Button disabled state: {disabled_state}")
        state_count = page.locator(f'[data-button-state="{state}"]').count() > 0
        logging.info(f"Button state '{state}' exists: {state_count}")
        return (disabled_state, state_count)
    except TimeoutError as e:
        logging.error(e)
        international_page(page)
        return True, True

def international_page(page):
    try:
        logging.info('trying to click international shopping USA link')
        page.locator("a.us-link:has(img[alt='United States'])").first.click()
        logging.info('clicked')
    
    except TimeoutError as e:
        logging.info('didnt find international link')
        
    
def start_scraping_page():
    logging.info('starting the scrape')
    vpn.vpn()
    browser, context, page = open_browser(PW)
    return load_page(browser, context, page, 'goto')

def scrape():
    
    browser, context, page = start_scraping_page()
    sku = LINK[-7:]
    button_disabled, is_soldout = check_button_state(page, sku, 'SOLD_OUT')
    
    while button_disabled and is_soldout:
        browser, context, page = load_page(browser, context, page, 'reload')
        button_disabled, is_soldout = check_button_state(page, sku, 'SOLD_OUT')
    
    button_disabled, is_add_cart = check_button_state(page, sku, 'ADD_TO_CART')
    if is_add_cart or not button_disabled:
        logging.info('Run to the store')
        send_notification("BUY", LINK)
    
    
    context.browser.close()
    PW.stop()

if __name__ == '__main__':
    scrape()
