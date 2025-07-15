import osmnx as ox

def download_city_graph(city_name, country="USA"):
    print(f"Downloading {city_name}...")
    G = ox.graph_from_place(f"{city_name}, {country}", network_type='drive')
    ox.save_graphml(G, f"../../data/{city_name.replace(',', '').replace(' ', '_')}_graph.graphml")
    print("Download & save complete.")
    return G

if __name__ == "__main__":
    download_city_graph("Cambridge, Massachusetts")