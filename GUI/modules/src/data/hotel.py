import csv
from typing import List, Optional


class Hotel:
    def __init__(
        self,
        name: str,
        stars: int,
        address: str,
        cadena: str,
        tarifa: str,
        price: float,
        hotel_url: str,
        destino: str,
    ):
        self.name = name
        self.stars = stars
        self.address = address
        self.cadena = cadena
        self.tarifa = tarifa
        self.price = price
        self.hotel_url = hotel_url
        self.destino = destino

    def __repr__(self):
        return f"Hotel({self.name}, {self.stars}*, {self.price} USD, {self.destino})"


def parse_price(price_str: str) -> Optional[float]:
    if not price_str or "No disponible" in price_str:
        return None
    try:
        return float(price_str.replace("USD", "").replace(",", "."))
    except Exception:
        return None


def load_hotels_from_csv(csv_path: str) -> List[Hotel]:
    hotels = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            price = parse_price(row["price"])
            try:
                stars = int(row["stars"])
            except Exception:
                stars = 0
            if price is not None and stars > 0:
                hotels.append(
                    Hotel(
                        name=row["name"],
                        stars=stars,
                        address=row["address"],
                        cadena=row["cadena"],
                        tarifa=row["tarifa"],
                        price=price,
                        hotel_url=row["hotel_url"],
                        destino=row["destino"],
                    )
                )
    return hotels
