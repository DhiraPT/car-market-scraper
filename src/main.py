from datetime import datetime
import os
from dotenv import load_dotenv
from supabase import create_client, Client

from msrp_scraper import scrape_msrp
from msrp_database_utils import write_msrp_database


load_dotenv()
URL: str = os.environ.get("SUPABASE_URL")
KEY: str = os.environ.get("SUPABASE_KEY")
EMAIL: str = os.environ.get("EMAIL")
PASSWORD: str = os.environ.get("PASSWORD")

MSRP_URL = 'https://www.sgcarmart.com/new_cars/newcars_listing.php?ORD=modelASC&PR1=0&PR2=&VT=Electric&RPG=60'
COE_URL = 'https://docs.google.com/spreadsheets/d/1Ma8dm_rdtdfNp8ONUG5ykFHwrEg1GFC3ObOMualMVBM/export?gid=0&format=csv'


def main():
    supabase: Client = create_client(URL, KEY)
    supabase.auth.sign_in_with_password({"email": EMAIL, "password": PASSWORD})
    # data, start_time = scrape_msrp(MSRP_URL)
    # for model in data:
    #     print(model.car_code)
    #     print(model.model_name)
    #     for submodel in model.submodels:
    #         print(submodel.subcode)
    #         print(submodel.submodel_name)
    #         print(submodel.coe_type)
    #         print(submodel.price_history)
    #     print()
    # write_msrp_database(supabase, data, start_time)
    # supabase.table('CarPrices').insert({
    #     'date': datetime.strptime('13-Jun-22', "%d-%b-%y").isoformat(),
    #     'submodel_id': 9028,
    #     'price': 100000
    # }).execute()
    # supabase.table('LastUpdates').insert({
    #     'data_title': 'COE',
    #     'updated_at': datetime.now().astimezone().isoformat()
    # }).execute()
    supabase.auth.sign_out()


if __name__ == "__main__":
    main()
