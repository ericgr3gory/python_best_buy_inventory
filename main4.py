from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            geolocation={"latitude": 36.2826, "longitude": -115.2914},
            permissions=["geolocation"],
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        # Load the page
        page.goto("https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=abcat0507002&id=pcat17071&iht=n&ks=960&list=y&qp=gpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)~NVIDIA%20GeForce%20RTX%205090&sc=Global&st=categoryid%24abcat0507002&type=page&usc=All%20Categories")

        # Grab each product container
        sku_items = page.query_selector_all(".sku-item")

        sku_details = []
        for product in sku_items:
            sku_id = product.get_attribute("data-sku-id") or "Unknown SKU"

            # 1) Product link (title <a>)
            link_el = product.query_selector("h4.sku-title a")
            if link_el:
                relative_url = link_el.get_attribute("href")  # e.g. "/site/..."
                product_url = (
                    "https://www.bestbuy.com" + relative_url
                    if relative_url and relative_url.startswith("/")
                    else relative_url
                )
            else:
                product_url = None

            # 2) "Add to Cart" (or "Sold Out") button text
            button = product.query_selector(".add-to-cart-button")
            button_text = button.inner_text().strip() if button else None

            # 3) Fulfillment summary text
            fulfillment_el = product.query_selector(".fulfillment-fulfillment-summary")
            fulfillment_text = (
                fulfillment_el.inner_text().strip()
                if fulfillment_el
                else None
            )

            sku_details.append({
                "skuId": sku_id,
                "productLink": product_url,
                "buttonText": button_text,
                "fulfillmentSummary": fulfillment_text
            })

        # Print results
        for item in sku_details:
            print(f"SKU: {item['skuId']}")
            print(f"  Product Link => {item['productLink']}")
            print(f"  Button Text  => {item['buttonText']}")
            print(f"  Fulfillment  => {item['fulfillmentSummary']}")
            print("--------------")

        browser.close()

if __name__ == "__main__":
    main()
