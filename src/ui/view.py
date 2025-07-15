import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulation.traffic_sim import simulate_traffic_and_scores
from simulation.optimizer import close_random_edge_and_evaluate, find_best_road_to_remove
import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt
import copy

st.title("Urban Planning AI: City Traffic & Pollution Simulator")
city_name = st.text_input("Enter city:", "Cambridge, Massachusetts")
run_sim = st.button("Load Map & Run Simulation")

if run_sim:
    with st.spinner('Preparing map...'):
        try:
            G = ox.graph_from_place(city_name, network_type='drive')
        except Exception as e:
            st.error(f"Could not download map for that city: {e}")
            st.stop()

        data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        abs_path = os.path.abspath(data_dir)
        os.makedirs(abs_path, exist_ok=True)
        graph_filename = f"{city_name.replace(',', '').replace(' ', '_')}_graph.graphml"
        graph_path = os.path.join(abs_path, graph_filename)
        ox.save_graphml(G, graph_path)
        st.session_state['graph_path'] = graph_path

    with st.spinner('Simulating realistic traffic...'):
        G_sim, top_edges, pollution, accessibility = simulate_traffic_and_scores(graph_path)
        st.session_state['base_sim'] = (G_sim, top_edges, pollution, accessibility)
        edge_colors = ["red" if (u, v, k) in top_edges else "lightgray" for u, v, k in G_sim.edges(keys=True)]
        fig_base, ax_base = ox.plot_graph(G_sim, node_size=0, edge_color=edge_colors, edge_linewidth=2, show=False, close=False)
        st.session_state['fig_base'] = fig_base
        st.success("Run completed. Ready for 'what-if' scenarios.")

if 'graph_path' in st.session_state and 'base_sim' in st.session_state:
    st.header("1️⃣ Interactive: Select a Road to Close & Compare")
    G_for_choices = ox.load_graphml(st.session_state['graph_path'])
    edge_list = [(u, v, k) for u, v, k in G_for_choices.edges(keys=True)]
    edge_labels = [f"{u}-{v}-{k}" for u, v, k in edge_list]
    selected = st.selectbox("Select edge to remove:", edge_labels)
    compare = st.button("Compare Before/After")

    if compare:
        idx = edge_labels.index(selected)
        edge_to_remove = [edge_list[idx]]
        G_after, top_after, pol_after, acc_after = simulate_traffic_and_scores(
            st.session_state['graph_path'], removed_edges=edge_to_remove
        )
        edge_colors_after = ["red" if (u, v, k) in top_after else "lightgray" for u, v, k in G_after.edges(keys=True)]
        fig_after, ax_after = ox.plot_graph(G_after, node_size=0, edge_color=edge_colors_after, edge_linewidth=2, show=False, close=False)

        st.subheader("Congestion Map Comparison:")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Original")
            st.pyplot(st.session_state['fig_base'])
            _, _, pol_base, acc_base = st.session_state['base_sim']
            st.markdown(f"**Pollution:** {pol_base:.0f} <br> **Accessibility:** {acc_base:.0f}", unsafe_allow_html=True)
        with col2:
            st.write(f"After Removing {selected}")
            st.pyplot(fig_after)
            st.markdown(f"**Pollution:** {pol_after:.0f} <br> **Accessibility:** {acc_after:.0f}", unsafe_allow_html=True)

    st.divider()

    st.header("2️⃣ 🤖 AI Suggestion: Best Road to Remove")
    metric = st.selectbox("Optimize for:", ["pollution", "accessibility"])
    if st.button("AI: Suggest Best Road to Remove"):
        with st.spinner("Calculating..."):
            result = find_best_road_to_remove(st.session_state['graph_path'], metric=metric)
            if result["best_edge"]:
                st.success(f"Best edge to remove for {metric}: {result['best_edge']}")
                st.write(f"Simulated {metric} after: {result['best_score']:.0f} | baseline: {result['base_score']:.0f}")
                st.info("Try removing that edge above and compare visually.")

    st.divider()

    st.header("3️⃣ Quick Random Road Closure Scenarios")
    if st.button("Random Road Closures & Evaluate"):
        suggestions = close_random_edge_and_evaluate(st.session_state['graph_path'], n_trials=3)
        for s in suggestions:
            st.write(f"Removed: {s['removed_edge']}")
            st.write(f"→ Pollution: {s['pollution']:.0f}\n→ Accessibility: {s['accessibility']:.0f}")
            if "error" in s:
                st.write(f"⚠️ {s['error']}")
else:
    st.info("Run the main simulation first to enable scenario tools.")