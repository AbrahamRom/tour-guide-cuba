import pandas as pd
import os
import re


def slugify(text):
    """Convierte texto a formato válido para nombres de archivo"""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "_", text)
    return text.strip("-_")


def split_tourism_data_by_destination(input_csv_path, output_dir):
    """
    Divide el CSV principal en archivos separados por destino
    """
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Leer el CSV completo
    df = pd.read_csv(input_csv_path, encoding="utf-8")

    # Obtener destinos únicos
    destinos = df["destino"].unique()

    print(f"Dividiendo datos en {len(destinos)} destinos...")

    for destino in destinos:
        # Filtrar hoteles por destino
        hotels_destino = df[df["destino"] == destino]

        # Crear nombre de archivo válido
        filename = f"{slugify(destino)}.csv"
        output_path = os.path.join(output_dir, filename)

        # Guardar CSV sin la columna destino (ya está implícita en el nombre)
        hotels_destino_clean = hotels_destino.drop("destino", axis=1)
        hotels_destino_clean.to_csv(output_path, index=False, encoding="utf-8")

        print(f"✓ {destino}: {len(hotels_destino)} hoteles → {filename}")

    print(f"\nArchivos guardados en: {output_dir}")
    return destinos


def get_available_destinations(destinations_dir):
    """Obtener lista de destinos disponibles desde el directorio"""
    if not os.path.exists(destinations_dir):
        return []

    destinations = []
    csv_files = [f for f in os.listdir(destinations_dir) if f.endswith(".csv")]

    for filename in csv_files:
        # Convertir nombre de archivo a nombre de destino
        destino = filename.replace(".csv", "").replace("_", " ").title()
        destinations.append(destino)

    return sorted(destinations)


if __name__ == "__main__":
    # Rutas por defecto para testing
    input_path = "../../../../DATA/tourism_data.csv"
    output_directory = "../../../../DATA/destinations/"

    if os.path.exists(input_path):
        split_tourism_data_by_destination(input_path, output_directory)
    else:
        print(f"Error: No se encontró el archivo {input_path}")
