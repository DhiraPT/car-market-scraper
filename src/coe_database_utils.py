from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo
import pandas as pd
from supabase import Client

from logger import get_logger


def get_coe_latest_date_in_database(db: Client) -> datetime | None:
    query_response = db.table('CoeBiddings').select('bidding_date').order('bidding_date', desc=True).limit(1).execute()
    data = query_response.data
    if len(data) == 0:
        return None
    return datetime.fromisoformat(data[0]['date'])


def write_coe_database(db: Client, df: pd.DataFrame, updated_at: datetime) -> None:
    print(f"{datetime.now(ZoneInfo('Asia/Singapore')).strftime("%Y-%m-%d %H:%M:%S")} - Writing COE data to database")
    latest_date = get_coe_latest_date_in_database(db)
    if latest_date is not None:
        df = df[df['Announcement Date'] > latest_date]

    for index, row in df.iterrows():
        db.table('CoeBiddings').insert({
            'coe_type': row['Category'],
            'bidding_date': row['Announcement Date'].isoformat(),
            'premium': row['Quota Premium'],
            'quota': row['Quota']
        }).execute()
        get_logger().info(f'New COE bidding inserted: coe_type={row["Category"]}, bidding_date={row["Announcement Date"].strftime("%Y-%m-%d")}, premium={row["Quota Premium"]}, quota={row["Quota"]}')
    
    db.table('LastUpdates').upsert({
        'data_title': 'COE',
        'updated_at': updated_at.isoformat()
    }).execute()
    get_logger().info(f'LastUpdates updated: data_title=COE, updated_at={updated_at.isoformat()}')

    print(f"{datetime.now(ZoneInfo('Asia/Singapore')).strftime("%Y-%m-%d %H:%M:%S")} - COE data written to database")
