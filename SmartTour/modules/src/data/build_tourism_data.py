import csv
import os
from src.crawler import CubaTravelCrawler
from split_tourism_data import slugify


def save_offers_to_csv(offers_dict, filename):
    # Unir todas las ofertas de todos los destinos en una sola lista
    all_offers = []
    for destino, offers in offers_dict.items():
        for offer in offers:
            offer_with_dest = offer.copy()
            offer_with_dest["destino"] = destino
            all_offers.append(offer_with_dest)
    if not all_offers:
        print("No se encontraron ofertas para guardar.")
        return
    # Obtener los campos del primer elemento
    fieldnames = list(all_offers[0].keys())
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_offers)
    print(f"Datos guardados en {filename}")


def save_offers_by_destination(offers_dict, output_dir):
    """Guardar ofertas directamente por destino"""
    os.makedirs(output_dir, exist_ok=True)

    for destino, offers in offers_dict.items():
        if not offers:
            print(f"No se encontraron ofertas para {destino}")
            continue

        # Crear nombre de archivo válido
        filename = f"{slugify(destino)}.csv"
        filepath = os.path.join(output_dir, filename)

        # Obtener campos del primer elemento
        fieldnames = list(offers[0].keys())

        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(offers)

        print(f"✓ {destino}: {len(offers)} ofertas → {filename}")


def main():
    url = "https://www.cuba.travel/"
    crawler = CubaTravelCrawler()
    try:
        results = crawler.crawl([url])

        # Opción 1: Guardar CSV único y luego dividir (compatibilidad hacia atrás)
        save_offers_to_csv(results, "../../../DATA/tourism_data.csv")

        # Opción 2: Guardar directamente por destinos (nuevo método)
        save_offers_by_destination(results, "../../../DATA/destinations/")

    finally:
        crawler.close()


if __name__ == "__main__":
    main()
