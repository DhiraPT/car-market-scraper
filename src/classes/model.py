from typing import List
from classes.submodel import Submodel


class Model:
    def __init__(self, model_name: str, car_code: int):
        self.model_name: str = model_name
        self.car_code: int = car_code
        self.submodels: List[Submodel] = []
        self.is_parallel_imported: bool = False

    def add_submodel(self, submodel: Submodel) -> None:
        self.submodels.append(submodel)
