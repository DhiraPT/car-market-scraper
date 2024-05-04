import ast
from datetime import datetime
import json
import re
from typing import List
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup
import math

from classes.model import Model
from classes.submodel import Submodel


def scrape_msrp(url: str) -> tuple[List[Model], datetime]:
    start_time = datetime.now().astimezone(tz=ZoneInfo('Asia/Singapore'))
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Scraping MSRP data from SGCarMart")
    # List to store the data
    data: List[Model] = []

    # Send a GET request to the URL
    client = requests.session()
    response = client.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        total_models = soup.find('span', class_='globalresults').get_text()
        total_pages = math.ceil(int(total_models.strip().split(' ')[0][1:]) / 60)

        data.extend(get_models_in_page(soup))

        if total_pages > 1:
            for page in range(1, total_pages):
                next_url = url + '&BRSR=' + str(page * 60)
                response = client.get(next_url)
                soup = BeautifulSoup(response.content, 'html.parser')
                data.extend(get_models_in_page(soup))

    for model in data:
        pricing_info_url = f'https://www.sgcarmart.com/new_cars/newcars_pricing.php?CarCode={model.car_code}'
        response = client.get(pricing_info_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            set_submodels_coe_type(model, soup)

        pricing_graph_url = f'https://www.sgcarmart.com/new_cars/newcars_pricing_submodels_graph.php?CarCode={model.car_code}&limit=48'
        response = client.get(pricing_graph_url)
        if response.status_code == 200:
            print(f"Getting price history for {model.model_name}")
            soup = BeautifulSoup(response.content, 'html.parser')

            script_tags = soup.find_all('script', type='text/javascript')
            price_history_exists = False
            for script_tag in script_tags:
                script_tag_text = script_tag.get_text()
                if 'google.load(\'visualization\',' in script_tag_text:
                    price_history_exists = True
                    break
                
            if not price_history_exists:
                print("No price history found")
                continue
            else:
                set_submodels_price_history(model, script_tag_text)

    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Scraped MSRP data")
    return data, start_time


# Get the models in the page
def get_models_in_page(soup: BeautifulSoup) -> List[Model]:
    models_data: List[Model] = []
    strong_tags = soup.find_all('strong')

    # Find parents <a> tags of <strong> tags where href contains the specified substring
    substring = "newcars_overview.php?CarCode="
    for strong_tag in strong_tags:
        parent_a_tag = strong_tag.find_parent('a', href=lambda href: href and substring in href)
        if parent_a_tag:
            model_name = strong_tag.get_text()
            model_url = parent_a_tag.get('href')
            car_code = int(model_url.split('CarCode=')[-1])
            models_data.append(Model(model_name, car_code))

    set_submodels_in_page_to_models(soup, models_data)

    return models_data


# Set the submodels of each model in the page
def set_submodels_in_page_to_models(soup: BeautifulSoup, models_data: List[Model]) -> None:
    input_tags = soup.find_all('input', {'name': 'SpecCode[]'})
    for input_tag in input_tags:
        onclick_value = input_tag.get('onclick')
        onclick_value = onclick_value.replace('checkboxActive(this.id,', '')[:-1]
        onclick_value = '[' + onclick_value + ']'
        onclick_value_list = ast.literal_eval(onclick_value)
        car_code = onclick_value_list[1]
        subcode = onclick_value_list[0]
        submodel_name = onclick_value_list[-1].replace('<span>(PI)</span>', '').strip()
        submodel = Submodel(submodel_name, subcode)

        # Add submodel to the corresponding model
        for model in models_data:
            if model.car_code == car_code:
                model.add_submodel(submodel)
                break


# Set the COE type of each submodel of the model
def set_submodels_coe_type(model: Model, soup: BeautifulSoup) -> None:
    a_tags = soup.find_all('a', href=lambda href: href and f'newcars_specs.php?CarCode={model.car_code}&Subcode=' in href)
    subcodes = [int(a_tag.get('href').split('Subcode=')[-1]) for a_tag in a_tags]

    category_texts = soup.find_all(string=re.compile('(Category [A-D] COE)'))
    coe_types = [category_text.strip().split('(Category ')[-1].replace(' COE)', '') for category_text in category_texts]

    for i in range(len(subcodes)):
        for submodel in model.submodels:
            if submodel.subcode == subcodes[i]:
                submodel.coe_type = coe_types[i]
                break

    for submodel in model.submodels:
        submodel.is_price_inclusive_of_coe = is_price_inclusive_of_coe(soup)

    model.is_parallel_imported = is_model_parallel_imported(soup)


# Check if the model is parallel imported
def is_model_parallel_imported(soup: BeautifulSoup) -> bool:
    string = soup.find(string='(Parallel Imported)')
    if string:
        return True
    return False


# Check if the price includes COE
def is_price_inclusive_of_coe(soup: BeautifulSoup) -> bool:
    span_tag = soup.find('span', class_='Newcars_Pricing_BigWord')
    if span_tag:
        parent_td_tag = span_tag.find_parent('td')
        if parent_td_tag:
            if 'w/o COE' in parent_td_tag.get_text():
                return False
    return True


# Set the price history of each submodel of the model
def set_submodels_price_history(model: Model, script_tag_text: str) -> None:
    submodel_column_pattern = r"data\.addColumn\('number', '(.*?)'\);"
    submodel_names = re.findall(submodel_column_pattern, script_tag_text)

    price_row_pattern = r"data\.addRows\(\[\s+\[(.*?)\]\s+\]\);"
    price_row = re.search(price_row_pattern, script_tag_text)
    price_row = price_row.group(1)
    price_row_by_date = price_row.split('],[')

    for i in range(len(price_row_by_date)):
        price_row_by_date[i] = '[' + price_row_by_date[i] + ']'
        prices_on_date = json.loads(price_row_by_date[i])
        date = None
        for j in range(len(prices_on_date)):
            if j == 0:
                date = prices_on_date[j]
            elif j % 2 == 1:
                if prices_on_date[j] is None:
                    continue
                submodel_name = submodel_names[j//2]
                for submodel in model.submodels:
                    if submodel.submodel_name == submodel_name:
                        submodel.add_price_history(date, prices_on_date[j])
                        break
