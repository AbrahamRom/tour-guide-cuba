from typing import List, Optional
from .hotel import Hotel, load_hotels_from_csv


class HotelRepository:
    def __init__(self, hotels: List[Hotel]):
        self.hotels = hotels

    @classmethod
    def from_csv(cls, csv_path: str):
        return cls(load_hotels_from_csv(csv_path))

    def get_hotels_by_destino(self, destino: str) -> List[Hotel]:
        return [h for h in self.hotels if h.destino == destino]

    def filter_hotels(
        self,
        destino: Optional[str] = None,
        max_price: Optional[float] = None,
        min_stars: Optional[int] = None,
    ) -> List[Hotel]:
        result = self.hotels
        if destino:
            result = [h for h in result if h.destino == destino]
        if max_price is not None:
            result = [h for h in result if h.price <= max_price]
        if min_stars is not None:
            result = [h for h in result if h.stars >= min_stars]
        return result
