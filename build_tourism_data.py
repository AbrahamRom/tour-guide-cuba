import csv
from src.crawler import CubaTravelCrawler


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
    with open(filename, mode="w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_offers)
    print(f"Datos guardados en {filename}")


def main():
    url = "https://www.cuba.travel/"
    crawler = CubaTravelCrawler()
    try:
        results = crawler.crawl([url])
        save_offers_to_csv(results, "tourism_data.csv")
    finally:
        crawler.close()


if __name__ == "__main__":
    main()
