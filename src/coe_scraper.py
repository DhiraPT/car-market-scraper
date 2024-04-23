from datetime import datetime

import pandas as pd


def scrape_coe(url: str) -> tuple[pd.DataFrame, datetime]:
    start_time = datetime.now().astimezone()
    df = pd.read_csv(url)

    df = df[['Announcement Date', 'Category', 'Quota Premium', 'Quota']]
    df['Announcement Date'] = pd.to_datetime(df['Announcement Date'], format='%d/%m/%Y')
    df['Quota'] = df['Quota'].str.replace(',', '').astype(int)
    df['Quota Premium'] = df['Quota Premium'].str.replace(',', '').str.replace('$', '').astype(int)
    df['Category'] = df['Category'].str[4]

    return df, start_time
