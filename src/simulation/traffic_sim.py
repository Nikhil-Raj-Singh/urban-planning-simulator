import networkx as nx
import osmnx as ox
import random
import copy

def simulate_traffic_and_scores(graph_path, num_trips=100, removed_edges=None):
    G = ox.load_graphml(graph_path)
    if removed_edges:
        G = copy.deepcopy(G)
        for u, v, k in removed_edges:
            if G.has_edge(u, v, k):
                G.remove_edge(u, v, k)
    nodes = list(G.nodes)
    if len(nodes) < 5:
        for u, v, k in G.edges(keys=True):
            G[u][v][k]['traffic'] = random.randint(0, 100)
    else:
        for u, v, k in G.edges(keys=True):
            G[u][v][k]['traffic'] = 0
        for _ in range(num_trips):
            src, tgt = random.sample(nodes, 2)
            try:
                path = nx.shortest_path(G, src, tgt, weight='length')
                for i in range(len(path) - 1):
                    keys = list(G[path[i]][path[i+1]].keys())
                    for k in keys:
                        G[path[i]][path[i+1]][k]['traffic'] += 1
            except (nx.NetworkXNoPath, KeyError):
                continue
    congested = sorted(
        G.edges(keys=True, data=True),
        key=lambda x: x[3].get('traffic', 0),
        reverse=True
    )[:5]
    top_edges = [(u, v, k) for u, v, k, d in congested]
    total_traffic = sum([d.get('traffic', 0) for u, v, k, d in G.edges(keys=True, data=True)])
    pollution = total_traffic * 1.2
    total_dist = 0
    valid_routes = 0
    for _ in range(10):
        src, tgt = random.sample(nodes, 2)
        try:
            path = nx.shortest_path(G, src, tgt, weight='length')
            d = sum([G[path[i]][path[i+1]][list(G[path[i]][path[i+1]].keys())[0]]['length'] for i in range(len(path)-1)])
            total_dist += d
            valid_routes += 1
        except (nx.NetworkXNoPath, KeyError):
            continue
    accessibility = (total_dist/valid_routes) if valid_routes else float('inf')
    return G, top_edges, pollution, accessibility