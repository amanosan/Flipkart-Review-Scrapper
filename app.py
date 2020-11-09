from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup as bs


app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        searchString = request.form['searchString'].replace(" ", "+")
        flipkart_base_url = "https://www.flipkart.com/search?q="
        flipkart_search_url = flipkart_base_url + searchString

        flipkart_page = requests.get(flipkart_search_url)

        if(flipkart_page.status_code == 200):
            flipkart_html = bs(flipkart_page.text, 'html.parser')

            # finding all the products:
            products = flipkart_html.findAll(
                'div', {'class': 'bhgxx2 col-12-12'})
            # limiting our products:
            products = products[4:10]

            # finding all the links from search
            links = []
            for product in products:
                link = product.div.div.div.a['href']
                links.append(link)

            # print(links)
            # Now finding all the reviews one by one:
            base_url = "https://www.flipkart.com"
            reviews = []
            for link in links:
                product_link = base_url + link
                product_page = requests.get(product_link)
                if (product_page.status_code == 200):
                    product_html = bs(product_page.text, "html.parser")
                    review_boxes = product_html.findAll(
                        'div', {'class': '_3nrCtb'})

                    # adding reviews in dictionary
                    for review_box in review_boxes:
                        # Name
                        try:
                            customer_name = review_box.find_all(
                                'p', {'class': '_3LYOAd _3sxSiS'})[0].text
                        except:
                            customer_name = "No Name"
                        # Rating:
                        try:
                            customer_rating = review_box.div.div.div.div.text
                        except:
                            customer_rating = 0
                        # Review Heading
                        try:
                            review_heading = review_box.div.div.div.p.text
                        except:
                            review_heading = 'No Heading'
                        # Review Message
                        try:
                            comment_tag = review_box.div.div.find_all(
                                'div', {'class': 'qwjRop'})
                            review_message = comment_tag[0].div.div.text
                        except:
                            review_message = "No Review"

                        reviewDict = {'Name': customer_name,
                                      "Rating": customer_rating,
                                      "Review Heading": review_heading,
                                      'Review': review_message}

                        # appending reviews in review list:
                        reviews.append(reviewDict)
                        # print(reviews)
                    return render_template('results.html', reviews=reviews)
        else:
            return "Something Went Wrong"
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
