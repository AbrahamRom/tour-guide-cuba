from typing import List, Optional, Dict
import os
import glob
from .hotel import Hotel, load_hotels_from_csv
from .split_tourism_data import slugify


class HotelRepository:
    def __init__(self, hotels: List[Hotel]):
        self.hotels = hotels
        # Crear índice por destino para búsquedas rápidas
        self._destino_index = {}
        for hotel in hotels:
            if hotel.destino not in self._destino_index:
                self._destino_index[hotel.destino] = []
            self._destino_index[hotel.destino].append(hotel)

    @classmethod
    def from_csv(cls, csv_path: str):
        """Mantener compatibilidad con CSV único"""
        return cls(load_hotels_from_csv(csv_path))

    @classmethod
    def from_destinations_directory(cls, destinations_dir: str):
        """Cargar hoteles desde directorio con CSVs por destino"""
        all_hotels = []

        # Buscar todos los archivos CSV en el directorio
        csv_files = glob.glob(os.path.join(destinations_dir, "*.csv"))

        if not csv_files:
            print(f"No se encontraron archivos CSV en {destinations_dir}")
            return cls([])

        for csv_file in csv_files:
            # Extraer nombre del destino del archivo
            filename = os.path.basename(csv_file)
            destino = filename.replace(".csv", "").replace("_", " ").title()

            # Cargar hoteles del CSV
            hotels = load_hotels_from_csv(csv_file)

            # Asignar destino a cada hotel
            for hotel in hotels:
                hotel.destino = destino

            all_hotels.extend(hotels)
            print(f"Cargados {len(hotels)} hoteles de {destino}")

        print(f"Total hoteles cargados: {len(all_hotels)}")
        return cls(all_hotels)

    @classmethod
    def from_single_destination(cls, destination_name: str, destinations_dir: str):
        """Cargar hoteles de un solo destino específico"""
        filename = f"{slugify(destination_name)}.csv"
        csv_path = os.path.join(destinations_dir, filename)

        if not os.path.exists(csv_path):
            available_files = [
                f.replace(".csv", "").replace("_", " ").title()
                for f in os.listdir(destinations_dir)
                if f.endswith(".csv")
            ]
            raise FileNotFoundError(
                f"No se encontró archivo para destino '{destination_name}'. Disponibles: {available_files}"
            )

        hotels = load_hotels_from_csv(csv_path)

        # Asignar destino a cada hotel
        for hotel in hotels:
            hotel.destino = destination_name

        return cls(hotels)

    def get_hotels_by_destino(self, destino: str) -> List[Hotel]:
        """Optimizado con índice"""
        return self._destino_index.get(destino, [])

    def get_available_destinations(self) -> List[str]:
        """Obtener lista de destinos disponibles"""
        return list(self._destino_index.keys())

    def filter_hotels(
        self,
        destino: Optional[str] = None,
        max_price: Optional[float] = None,
        min_stars: Optional[int] = None,
    ) -> List[Hotel]:
        if destino:
            result = self.get_hotels_by_destino(destino)
        else:
            result = self.hotels

        if max_price is not None:
            result = [h for h in result if h.price <= max_price]
        if min_stars is not None:
            result = [h for h in result if h.stars >= min_stars]
        return result
