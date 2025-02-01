from playwright.sync_api import sync_playwright ,TimeoutError
from time import sleep
import os
from dotenv import load_dotenv
import requests

load_dotenv()
LINK = os.getenv('BEST_BUY_LINK')
#LINK_5000 = os.getenv('BEST_BUY_LINK_5000')
#LINK = os.getenv('BEST_BUY_LINK_TEST')
#LINK = os.getenv('BEST_BUY_giga_5090'):
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


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False,  # Run headless mode
            args=["--use-fake-ui-for-media-stream"]  # Force geolocation permission
        )
        context = browser.new_context(
            #geolocation={"latitude": 36.1699, "longitude": -115.1398},  # Las Vegas
            #geolocation={"latitude": 36.2553, "longitude": -115.6350},  # Mount Charleston
            geolocation={"latitude": 36.2826, "longitude": -115.2914},  # Centennial Hills
            permissions=["geolocation"]
        )
        page = context.new_page()
        page.goto(LINK)
        sku = (LINK[-7:])
        
        button = page.locator(f"[data-sku-id='{sku}']") #5090
        button_status = page.locator('data-button-state="COMING_SOON"')
        while button.is_disabled() and button_status:
            
            for _ in range(2):
                if button.is_disabled() and button_status:
                    print("Button is disabled!")
                    sleep(2)
            sleep(3)
            try: 
                page.reload()
                print('reload')
            
            except TimeoutError:
                print('timeout')
            
        button_status = page.locator('data-button-state="ADD_TO_CART"')
        print(button.is_enabled())
        print(button_status)
        
        if (button.is_enabled() and button_status):
            print('run to the store')
            send_notification("BUY", LINK)
        sleep(2)
        browser.close()
if __name__ == '__main__':
        
    
    main()