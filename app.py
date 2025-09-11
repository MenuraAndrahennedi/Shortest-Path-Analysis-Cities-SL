from __future__ import annotations

import streamlit as st
from streamlit.components.v1 import html

from core.graph import load_graph
from service.run_all import run_all
from core.vizualize import map_to_html

st.set_page_config(page_title="Shortest Path Algorithm Analysis", layout="wide")
st.title("Shortest Path Algorithm Analysis")


# ---------------- Settings Bar ----------------
with st.sidebar:
    st.header("Settings")
    undirected = st.toggle("Treat roads as undirected (two-way)", value=True)
    st.caption("Tip: If a city pair shows “No path found”, enable two-way roads.")


# ---------- Load graph (cached) ---------
@st.cache_data(show_spinner=False)
def load_graph_data(undirected_flag: bool):
    nodes, adj = load_graph(undirected=undirected_flag)
    ids = list(nodes.keys())
    labels = {node_id: f"{nodes[node_id]['name']} ({node_id})" for node_id in ids}
    return nodes, adj, ids, labels

nodes, adj, ids, labels = load_graph_data(undirected)


# ---------------- Source, Target, and Mode Selection ----------------
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    src_id = st.selectbox("Source", options=ids, format_func=lambda x: labels[x], index=0)
with c2:
    dst_id = st.selectbox("Target", options=ids, format_func=lambda x: labels[x], index=1)
with c3:
    mode = st.radio("Mode of shortest path", ["Distance (km)", "Travel time (min)"], index=0)
    weight_key = "distance_km" if mode.startswith("Distance") else "travel_time_min"

go = st.button("Compute routes", type="primary")


# ---------------- Total Distance and Time ----------------
def total_distance_km(path_ids, adjacency) -> float:
    total = 0.0
    for i in range(len(path_ids) - 1):
        u, v = path_ids[i], path_ids[i + 1]
        found = False
        for neighbor in adjacency.get(u, []):
            if neighbor[0] == v:
                total += float(neighbor[1])  # distance_km
                found = True
                break
        if not found:
            for neighbor in adjacency.get(v, []):
                if neighbor[0] == u:
                    total += float(neighbor[1])
                    break
    return total

def total_time_min(path_ids, adjacency) -> float:
    total = 0.0
    for i in range(len(path_ids) - 1):
        u, v = path_ids[i], path_ids[i + 1]
        found = False
        for neighbor in adjacency.get(u, []):
            if neighbor[0] == v:
                total += float(neighbor[2])  # travel_time_min
                found = True
                break
        if not found:
            for neighbor in adjacency.get(v, []):
                if neighbor[0] == u:
                    total += float(neighbor[2])
                    break
    return total


# ---------------- Run Algorithms and Show Maps ----------------
if go:
    nodes_used, results, maps = run_all(
        start=src_id,
        goal=dst_id,
        weight_key=weight_key,
        undirected=undirected,
        return_maps=True,
    )
    order = ["A*", "Dijkstra", "Bellman-Ford"]
    col_A, col_D, col_B = st.columns(3)
    cols = [col_A, col_D, col_B]

    for col, name in zip(cols, order):
        result = next((x for x in results if x["algorithm"] == name), None)

        with col:
            st.subheader(name)

            with st.container(border=True):
                if result is None:
                    st.error("No result.")
                    continue

                # Map 
                html(map_to_html(maps[name]), height=420)

                # Algorithm runtime (ms)
                st.markdown(f"**Computation time:** `{result['runtime_sec'] * 1000:.1f} ms`")

                # Display other details
                if result["path"]:
                    total_km  = total_distance_km(result["path"], adj)
                    total_min = total_time_min(result["path"], adj)

                    st.markdown(f"**Total Distance:** `{total_km:.3f} km`")
                    st.markdown(f"**Total Time:** `{total_min:.2f} min`")

                    # Stops (traveling city list)
                    stops = " → ".join(nodes_used[n]["name"] for n in result["path"])
                    st.markdown(f"**Stops:** {stops}")
                else:
                    st.markdown("**Total Distance:** `N/A`")
                    st.markdown("**Total Time:** `N/A`")
                    st.warning("No path found for this algorithm.")

else:
    st.info("Pick a Source and Destination, then click **Compute routes**.")




