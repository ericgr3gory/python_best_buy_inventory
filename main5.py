from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=abcat0507002&id=pcat17071&iht=n&ks=960&list=y&qp=gpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)~NVIDIA%20GeForce%20RTX%205080&sc=Global&st=categoryid%24abcat0507002&type=page&usc=All%20Categories")


        sku_items = page.query_selector_all(".sku-item")
        for product in sku_items:
            sku_id = product.get_attribute("data-sku-id")
            button = product.query_selector(".add-to-cart-button")
            
            if button:
                # Method 1: Check Playwright’s is_enabled()
                if button.is_enabled():
                    button_text = button.inner_text().strip()
                    print(f"SKU={sku_id}: button text = '{button_text}', button is enabled.")
                else:
                    print(f"SKU={sku_id}: button is disabled.")
            else:
                print(f"SKU={sku_id}: No add-to-cart button found.")
        
        browser.close()

if __name__ == "__main__":
    main()
