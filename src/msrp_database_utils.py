from datetime import datetime
from typing import List
from supabase import Client

from classes.model import Model
from classes.submodel import Submodel
from logger import get_logger


def get_models_in_database(db: Client) -> List[dict]:
    query_response = db.table('CarModels').select('model_id').execute()
    data = query_response.data
    return data


def get_submodels_in_database(db: Client) -> List[dict]:
    query_response = db.table('CarSubmodels').select('submodel_id').execute()
    data = query_response.data
    return data


def write_msrp_database(db: Client, data: List[Model], updated_at: datetime) -> None:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Writing MSRP data to database")
    existing_models = get_models_in_database(db)
    existing_submodels = get_submodels_in_database(db)
    for model in data:
        insert_car_model(db, model, existing_models)
        for submodel in model.submodels:
            insert_car_submodel(db, model, submodel, existing_submodels)
            insert_car_submodel_prices(db, submodel)
    
    db.table('LastUpdates').upsert({
        'data_title': 'MSRP',
        'updated_at': updated_at.isoformat()
    }).execute()
    get_logger().info(f'LastUpdates updated: data_title=MSRP, updated_at={updated_at.isoformat()}')

    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - MSRP data written to database")


def insert_car_model(db: Client, model: Model, existing_models: List[dict]) -> None:
    if any(model.car_code == existing_model['model_id'] for existing_model in existing_models):
        return
    db.table('CarModels').insert({
        'model_id': model.car_code,
        'model': model.model_name,
        'is_parallel_imported': model.is_parallel_imported
    }).execute()
    get_logger().info(f'New model inserted: model_id={model.car_code}, model={model.model_name}, is_parallel_imported={model.is_parallel_imported}')


def insert_car_submodel(db: Client, model: Model, submodel: Submodel, existing_submodels: List[dict]) -> None:
    if any(submodel.subcode == existing_submodel['submodel_id'] for existing_submodel in existing_submodels):
        return
    db.table('CarSubmodels').insert({
        'model_id': model.car_code,
        'submodel_id': submodel.subcode,
        'submodel': submodel.submodel_name,
        'coe_type': submodel.coe_type,
    }).execute()
    get_logger().info(f'New submodel inserted: submodel_id={submodel.subcode}, submodel={submodel.submodel_name}, model_id={model.car_code}, coe_type={submodel.coe_type}')


def insert_car_submodel_prices(db: Client, submodel: Submodel) -> None:
    query_response = db.table('CarPrices').select('date').eq('submodel_id', submodel.subcode).order('date', desc=True).limit(1).execute()
    data = query_response.data
    latest_date = None
    if len(data) > 0:
        latest_date = datetime.fromisoformat(data[0]['date'])
        if latest_date == submodel.price_history[-1][1]:
            return
    for date, price in submodel.price_history:
        if latest_date != None and date <= latest_date:
            continue
        db.table('CarPrices').insert({
            'submodel_id': submodel.subcode,
            'date': date.isoformat(),
            'price': price,
            'is_coe_included': submodel.is_price_inclusive_of_coe
        }).execute()
        get_logger().info(f'New price inserted: submodel_id={submodel.subcode}, date={date.strftime("%Y-%m-%d")}, price={price}, is_coe_included={submodel.is_price_inclusive_of_coe}')
