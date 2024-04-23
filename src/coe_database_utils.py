from datetime import datetime
from typing import List
import pandas as pd
from supabase import Client

from logger import get_logger


def get_coe_latest_date_in_database(db: Client) -> List[tuple[int, datetime]]:
    query_response = db.table('CoeBiddings').select('date').order('date', ascending=False).limit(1).execute()
    data = query_response['data']
    return datetime.fromisoformat(data[0]['date'])


def write_coe_database(db: Client, df: pd.DataFrame, updated_at: datetime) -> None:
    latest_date = get_coe_latest_date_in_database(db)
    df = df[df['Announcement Date'] > latest_date]
    for index, row in df.iterrows():
        db.table('CoeBiddings').insert({
            'coe_type': row['Category'],
            'bidding_date': row['Announcement Date'].isoformat(),
            'premium': row['Quota Premium'],
            'quota': row['Quota']
        }).execute()
        get_logger().info(f'New COE bidding inserted: coe_type={row["Category"]}, bidding_date={row["Announcement Date"].isoformat()}, premium={row["Quota Premium"]}, quota={row["Quota"]}')
    
    db.table('LastUpdates').upsert({
        'data_title': 'COE',
        'updated_at': updated_at.isoformat()
    }).execute()
    get_logger().info(f'LastUpdates updated: data_title=COE, updated_at={updated_at.isoformat()}')


def get_coe_premium(db: Client, coe_type: str, date: datetime) -> int:
    query_response = db.table('CoeBiddings').select('premium').eq('coe_type', coe_type).eq('bidding_date', date.isoformat()).execute()
    data = query_response['data']
    return data[0]['premium']
