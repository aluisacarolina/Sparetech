import asyncio
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

def extract_product_info(product_container, part_type):
    product_id = product_container['data-product-id']  

    product_name = product_container.find("h2", class_="heading").text.strip()

    # Check if the "span" element with class "price" exists
    price_element = product_container.find("span", class_="price")
    if price_element:
        product_price = price_element.text.strip()
    else:
        return None  # Skip products without a price

    product_brand = "Bosch" 
    product_category = part_type.capitalize()  
    product_dimension = product_container.find("p", class_="e-stock-info").text.strip()
    product_description = product_container.find("div", class_="details").find("p").text.strip()

    return {
        'Product ID': product_id,
        'Product Name': product_name,
        'Price': product_price,
        'Brand': product_brand,
        'Category': product_category,
        'Product Dimension': product_dimension,
        'Description': product_description
    }

def scrape_page(url, context, part_type):
    page = context.new_page()
    page.goto(url)
    page.wait_for_selector('.product.ee-product')

    soup = BeautifulSoup(page.content(), 'html.parser')
    product_containers = soup.find_all("li", class_="product ee-product")

    page.close()

    return [extract_product_info(product_container, part_type) for product_container in product_containers if extract_product_info(product_container, part_type)]

def scrape_all_pages(base_urls):
    all_products = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        for part_type, base_url in base_urls.items():
            page = 1
            while True:
                url = f"{base_url}?page={page}"
                product_data = scrape_page(url, context, part_type)
                if not product_data:
                    break
                all_products.extend(product_data)
                page += 1

        browser.close()

    return all_products

base_urls = {
    'Motors': "https://www.espares.co.uk/search/ma856pt1552/fridges-and-freezers/motor/bosch",
    'Valves': "https://www.espares.co.uk/search/ma856pt1884/fridges-and-freezers/valves/bosch",
}

all_products_data = scrape_all_pages(base_urls)

# Create a DataFrame
df = pd.DataFrame(all_products_data)

# Save the DataFrame to Excel with the desired name
excel_path = r'C:\Users\lsutilfr\OneDrive - NTT DATA EMEAL\Documentos\python_scripts\Fridges&Freezers_parts_data.xlsx'
df.to_excel(excel_path, index=False)

print(f"Excel file saved successfully at: {excel_path}")
