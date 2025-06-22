from simulator.chatbot_sim import run_chatbot_simulation
from simulator.rag_sim import simulate_rag_interaction
from simulator.searcher_sim import simulate_search_query
from simulator.planner_sim import run_planner
from simulator.recommender_sim import simulate_recommendation

# Dictionary-based dispatcher
def run_simulation(module, **kwargs):
    if module == "chatbot":
        return run_chatbot_simulation(**kwargs)
    elif module == "rag":
        return simulate_rag_interaction(**kwargs)
    elif module == "searcher":
        return simulate_search_query(**kwargs)
    elif module == "planner":
        return run_planner(**kwargs)
    elif module == "recommender":
        return simulate_recommendation(**kwargs)
    else:
        raise ValueError(f"Unknown module: {module}")
