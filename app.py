from flask import Flask, request
from bs4 import BeautifulSoup
import requests
import csv
from flask import render_template

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def home():
    data = []
    if request.method == 'POST':
        url = request.form['shop_url']
        print(url)
        with open('etsy_urls.csv', mode='w', newline='') as output_file:
            writer = csv.writer(output_file)

            response = requests.get(url)
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            product_elements = soup.find_all("div", {"class": "v2-listing-card"})
            for product_element in product_elements:
                product_url = product_element.find("a", {"class": "listing-link"})['href']
                product_title = product_element.find("h3", {"class": "text-gray text-truncate mb-xs-0 text-body"})
                product_price = product_element.find("p",
                                                     {"class": "text-gray-lighter text-truncate mt-xs-0 text-body"})
                writer.writerow(
                    [product_url, product_title, product_price])

        with open('etsy_urls.csv', 'r') as file:
            reader = csv.reader(file)
            data = [row for row in reader]
    return render_template('home.html', data=data)


@app.route("/etsy")
def etsy():
    data_list = []
    with open('etsy-ursl.csv', mode='r') as csv_file, \
            open('etsy_product_data.csv', mode='w', newline='') as output_file:

        writer = csv.writer(output_file)
        writer.writerow(
            ["SL", "Title", "Description", "Price", "Price SKU", "QUANTITY", "TAGS", "MATERIALS", "Image",
             "Variation 1 Type",
             "Variation 1 Name", "Variation 1 Values", "Variation 2 Type", "Variation 2 Name", "Variation 2 Values",
             "SKU Data Listing ID", "Price SKU", "Product URL"])

        reader = csv.reader(csv_file)
        # Loop through each row in the Etsy CSV file and convert it to Shopify format
        for csvrow in reader:
            # Skip the header row
            if reader.line_num == 1:
                continue

            # The URL of the product page to scrape
            print(csvrow[0], reader.line_num)
            url = csvrow[0]
            response = requests.get(url)
            html_content = response.text

            # Create a BeautifulSoup object from the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find the title of the product
            try:
                product_title = soup.find("h1", {
                    "class": "wt-text-body-01 wt-line-height-tight wt-break-word wt-mt-xs-1"}).getText()
            except:
                product_title = ""

            Description = soup.find("p", {"class": "wt-text-body-01 wt-break-word"})
            Price = soup.find("p", {"class": "wt-text-title-03 wt-mr-xs-1"}).getText()
            SKU = ""
            QUANTITY = ""
            TAGS = ""
            MATERIALS = ""
            prices = []
            if "+" in Price:
                SKU = "SKU with price"
            images = []
            image_elements = soup.find_all("img",
                                           {"class": "wt-max-width-full wt-horizontal-center wt-vertical-center "
                                                     "carousel-image wt-rounded"})
            for image_element in image_elements:
                images.append(image_element['data-src-zoom-image'])

            listingId = soup.find("input", {"name": "listing_id"})['value']
            URL = url
            # Find the div containing the variant options (assuming it has a class of 'variations')
            variant_div = soup.find('div', attrs={'data-selector': 'listing-page-variations'})
            selects = variant_div.find_all('select')
            option_name = ""
            option2_name = ""
            optionvalues = []
            optionvalues2 = []
            i = 0
            for select in selects:
                i = i + 1
                label_element = soup.find('label', {'for': '{}'.format(select['id'])})
                if i == 1:
                    option_name = label_element.text
                else:
                    option2_name = label_element.text
                options = select.find_all('option')
                for option in options:
                    if option.text.strip() != 'Select an option':
                        if i == 1:
                            optionvalues.append(option.text.strip())
                        else:
                            optionvalues2.append(option.text.strip())

                writer.writerow(
                    [reader.line_num, product_title, Description, Price, SKU, QUANTITY, TAGS, MATERIALS, images,
                     "", option_name, optionvalues, "", option2_name, optionvalues2, listingId, Price, URL])

    with open('etsy_product_data.csv', 'r') as file:
        reader = csv.reader(file)
        data = [row for row in reader]
    return render_template('product-list.html', data=data)
