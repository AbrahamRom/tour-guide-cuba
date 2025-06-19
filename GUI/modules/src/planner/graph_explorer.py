from typing import List, Optional
from ..data.hotel_repository import HotelRepository
from .graph_node import GraphNode


class GraphExplorer:
    def __init__(
        self, hotel_repo: HotelRepository, nights: int, budget: float, destino: str
    ):
        self.hotel_repo = hotel_repo
        self.nights = nights
        self.budget = budget
        self.destino = destino

    def expand_node(self, node: GraphNode) -> List[GraphNode]:
        """
        Dado un nodo, genera los posibles siguientes nodos (hoteles para la siguiente noche)
        """
        if node.night >= self.nights:
            return []
        next_night = node.night + 1
        options = []
        for hotel in self.hotel_repo.get_hotels_by_destino(self.destino):
            if hotel.price <= node.budget_left:
                new_path = node.path + [(next_night, hotel)]
                options.append(
                    GraphNode(
                        night=next_night,
                        hotel=hotel,
                        budget_left=node.budget_left - hotel.price,
                        stars_accum=node.stars_accum + hotel.stars,
                        path=new_path,
                    )
                )
        # Ordenar por estrellas (descendente) y luego por mejor relación estrellas/precio
        options.sort(
            key=lambda n: (n.hotel.stars, n.hotel.stars / n.hotel.price),
            reverse=True,
        )
        return options

    def search_best_path(self) -> Optional[GraphNode]:
        """
        Busca el camino de mayor suma de estrellas dentro del presupuesto.
        """
        best_node = None
        stack = []
        # Inicializar con todos los hoteles posibles para la primera noche
        for hotel in self.hotel_repo.get_hotels_by_destino(self.destino):
            if hotel.price <= self.budget:
                node = GraphNode(
                    night=1,
                    hotel=hotel,
                    budget_left=self.budget - hotel.price,
                    stars_accum=hotel.stars,
                    path=[(1, hotel)],
                )
                stack.append(node)
        while stack:
            node = stack.pop()
            if node.night == self.nights:
                if best_node is None or node.stars_accum > best_node.stars_accum:
                    best_node = node
            else:
                stack.extend(self.expand_node(node))
        return best_node
