import requests
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
from config import country_code_map

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    status = None  # Initialize status variable before the condition
    page_name = None
    if request.method == 'POST':
        # Get the data from the form
        url = request.form['url']
        country = request.form['country']
        parsed_url = urlparse(url)
        base_url = parsed_url.netloc
        path = parsed_url.path
        country_code = country_code_map.get(country, "")
        if country_code:
            modified_url = f"{parsed_url.scheme}://{base_url}/{country_code}{path}"
        else:
            modified_url = url
        print(f"Validating {modified_url} for checking connection")
        try:
            # Perform the GET request to the provided URL
            response = requests.get(modified_url)
            if response.status_code == 200:
                status = "Success"
                soup = BeautifulSoup(response.text, 'html.parser')
                element = soup.find('div', class_='CoveoForSitecoreContext')
                if element:
                    page_name = element.get('data-sc-page-name-full-path', 'Attribute not found')
                else:
                    page_name = "Element not found"
                page_name_splitdata = page_name.split('/')
                try:
                    last_part = int(page_name_splitdata[-1])
                    if last_part == 404:
                        status = "Page doesn't exist, try with a valid URL"
                    else:
                        status = "Success"
                except ValueError:
                    # If the last part is not an integer, handle it gracefully
                    status = "Success"  # Or another appropriate message


        except requests.exceptions.RequestException as e:
            # If the request fails, show the error message
            status = f"Error: {e}"

    return render_template('home_page.html', status=status, page_name=page_name)


if __name__ == '__main__':
    app.run(debug=True)
