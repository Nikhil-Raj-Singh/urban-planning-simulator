from simulation.traffic_sim import simulate_traffic_and_scores
import osmnx as ox
import random

def close_random_edge_and_evaluate(graph_path, n_trials=3):
    G = ox.load_graphml(graph_path)
    all_edges = list(G.edges(keys=True))
    suggestions = []
    random.shuffle(all_edges)
    for i in range(min(n_trials, len(all_edges))):
        test_edge = all_edges[i]
        try:
            _, _, pollution, accessibility = simulate_traffic_and_scores(graph_path, removed_edges=[test_edge])
            suggestions.append({
                "removed_edge": test_edge,
                "pollution": pollution,
                "accessibility": accessibility
            })
        except Exception as e:
            suggestions.append({
                "removed_edge": test_edge,
                "pollution": float('inf'),
                "accessibility": float('inf'),
                "error": str(e)
            })
    return suggestions

def find_best_road_to_remove(graph_path, metric="pollution", sample_size=20):
    G = ox.load_graphml(graph_path)
    all_edges = list(G.edges(keys=True))
    try_edges = random.sample(all_edges, min(sample_size, len(all_edges)))
    best_edge = None
    best_score = None
    _, _, base_pollution, base_accessibility = simulate_traffic_and_scores(graph_path)
    for edge in try_edges:
        try:
            _, _, pollution, accessibility = simulate_traffic_and_scores(graph_path, removed_edges=[edge])
            score = pollution if metric == "pollution" else accessibility
            if best_score is None or score < best_score:
                best_score = score
                best_edge = edge
        except Exception:
            continue
    return {
        "best_edge": best_edge,
        "metric": metric,
        "best_score": best_score,
        "base_score": base_pollution if metric=="pollution" else base_accessibility
    }