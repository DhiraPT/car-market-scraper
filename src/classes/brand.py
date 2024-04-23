from typing import List
from classes.model import Model


class Brand:
    def __init__(self, brand_name: str):
        self.brand_name: str = brand_name
        self.models: List[Model] = []

    def add_model(self, model: Model) -> None:
        self.models.append(model)
