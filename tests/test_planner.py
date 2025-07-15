import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "SmartTour"))
)
from modules.src.data.hotel_repository import HotelRepository
from modules.src.planner.graph_explorer import GraphExplorer


def test_planner():
    # Usar el nuevo sistema de directorios
    destinations_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "DATA", "destinations")
    )

    # Probar carga desde directorio completo
    repo = HotelRepository.from_destinations_directory(destinations_dir)

    # Probar carga de destino específico
    repo_specific = HotelRepository.from_single_destination(
        "La Habana", destinations_dir
    )

    nights = 2
    budget = 100.0
    destino = "La Habana"

    explorer = GraphExplorer(repo_specific, nights, budget, destino)
    best_node = explorer.search_best_path()
    assert (
        best_node is not None
    ), "No se encontró una secuencia válida dentro del presupuesto."
    assert len(best_node.path) == nights, f"La secuencia debe tener {nights} noches."
    assert best_node.stars_accum > 0, "La suma de estrellas debe ser mayor que 0."
    for night, hotel in best_node.path:
        assert (
            hotel.price <= budget
        ), "El precio de cada hotel debe ser menor o igual al presupuesto."
        assert hotel.destino == destino, "El destino del hotel debe coincidir."
    # El presupuesto restante debe ser >= 0
    assert (
        best_node.budget_left >= 0
    ), "El presupuesto restante debe ser mayor o igual a 0."
    print(f"Test exitoso: {best_node.stars_accum} estrellas acumuladas")
    print(f"Presupuesto restante: ${best_node.budget_left:.2f}")


def test_multiple_destinations():
    """Test para verificar carga de múltiples destinos"""
    destinations_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "DATA", "destinations")
    )

    repo = HotelRepository.from_destinations_directory(destinations_dir)
    destinations = repo.get_available_destinations()

    assert len(destinations) > 0, "Debe haber al menos un destino disponible"
    print(f"Destinos encontrados: {destinations}")

    for destino in destinations:
        hotels = repo.get_hotels_by_destino(destino)
        assert len(hotels) > 0, f"Destino {destino} debe tener hoteles"
        print(f"{destino}: {len(hotels)} hoteles")


def test_single_destination_load():
    """Test para verificar carga de un solo destino"""
    destinations_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "DATA", "destinations")
    )

    # Test con destino existente
    repo = HotelRepository.from_single_destination("La Habana", destinations_dir)
    hotels = repo.get_hotels_by_destino("La Habana")
    assert len(hotels) > 0, "La Habana debe tener hoteles"

    # Test con destino inexistente
    try:
        HotelRepository.from_single_destination("Destino Inexistente", destinations_dir)
        assert False, "Debería lanzar FileNotFoundError"
    except FileNotFoundError as e:
        print(f"Error esperado: {e}")
        assert "No se encontró archivo" in str(e)


if __name__ == "__main__":
    test_planner()
    test_multiple_destinations()
    test_single_destination_load()
    print("✅ Todos los tests pasaron!")
