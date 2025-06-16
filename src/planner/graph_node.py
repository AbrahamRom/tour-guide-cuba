from typing import List, Tuple
from src.data.hotel import Hotel


class GraphNode:
    def __init__(
        self,
        night: int,
        hotel: Hotel,
        budget_left: float,
        stars_accum: int,
        path: List[Tuple[int, Hotel]],
    ):
        self.night = night
        self.hotel = hotel
        self.budget_left = budget_left
        self.stars_accum = stars_accum
        self.path = path  # List of (night, hotel)

    def __repr__(self):
        return f"GraphNode(night={self.night}, hotel={self.hotel.name}, budget_left={self.budget_left}, stars_accum={self.stars_accum})"
