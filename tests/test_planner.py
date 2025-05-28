import os
from src.data.hotel_repository import HotelRepository
from src.planner.graph_explorer import GraphExplorer


def test_planner():
    # Ruta al archivo CSV de hoteles
    csv_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "tourism_data.csv")
    )
    repo = HotelRepository.from_csv(csv_path)
    nights = 2
    budget = 100.0
    destino = "La Habana"
    explorer = GraphExplorer(repo, nights, budget, destino)
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
