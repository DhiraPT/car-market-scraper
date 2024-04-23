from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client

from coe_database_utils import write_coe_database
from coe_scraper import scrape_coe
from logger import create_logger, upload_log_file
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
    # Connect to Supabase
    supabase: Client = create_client(URL, KEY)
    supabase.auth.sign_in_with_password({"email": EMAIL, "password": PASSWORD})

    # Create a logger
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.log'
    create_logger(filename)

    # Scrape and write to database
    df, start_time_coe = scrape_coe(COE_URL)
    write_coe_database(supabase, df, start_time_coe)
    data, start_time_msrp = scrape_msrp(MSRP_URL)
    write_msrp_database(supabase, data, start_time_msrp)
    # supabase.table('CarPrices').insert({
    #     'date': datetime.strptime('13-Jun-22', "%d-%b-%y").isoformat(),
    #     'submodel_id': 9028,
    #     'price': 100000
    # }).execute()
    # supabase.table('LastUpdates').insert({
    #     'data_title': 'COE',
    #     'updated_at': datetime.now().astimezone().isoformat()
    # }).execute()
    upload_log_file(supabase, filename)
    supabase.auth.sign_out()


if __name__ == "__main__":
    main()
