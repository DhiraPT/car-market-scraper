from datetime import datetime
from typing import List


class Submodel:
    def __init__(self, submodel_name: str, subcode: int):
        self.submodel_name: str = submodel_name
        self.subcode: int = subcode
        self.coe_type: str | None = None
        self.is_price_include_coe: bool = True
        self.price_history: List[tuple[datetime, str]] = []

    def add_price_history(self, date_string: str, price: int) -> None:
        date = datetime.strptime(date_string, '%d-%b-%y')
        self.price_history.append((date, price))
