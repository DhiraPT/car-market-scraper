from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd


def scrape_coe(url: str) -> tuple[pd.DataFrame, datetime]:
    start_time = datetime.now().astimezone(tz=ZoneInfo('Asia/Singapore'))
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Scraping COE data from {url}")
    df = pd.read_csv(url)

    df = df[['Announcement Date', 'Category', 'Quota Premium', 'Quota']]
    df['Announcement Date'] = pd.to_datetime(df['Announcement Date'], format='%d/%m/%Y')
    df['Quota'] = df['Quota'].str.replace(',', '').astype(int)
    df['Quota Premium'] = df['Quota Premium'].str.replace(',', '').str.replace('$', '').astype(int)
    df['Category'] = df['Category'].str[4]

    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Scraped {len(df)} COE data")
    return df, start_time
