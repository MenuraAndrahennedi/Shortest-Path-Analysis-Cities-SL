from __future__ import annotations

import streamlit as st, pathlib
from streamlit.components.v1 import html

from core.graph import load_graph
from service.run_all import run_all
from core.vizualize import map_to_html

st.set_page_config(page_title="Shortest Path Algorithm Analysis", layout="wide")

st.divider()
st.title("Shortest Path Algorithm Analysis")
st.markdown("#### Compare algorithms on real Sri Lankan road networks")
st.divider()

with st.container(border=True, width=1000):
    col1, col2= st.columns([8,7])
    with col1:
        undirected = st.toggle("Treat roads as undirected (two-way)", value=True, help="If enabled, all roads are treated as two-way regardless of their actual direction.")
        st.caption("Tip: If a city pair shows “No path found”, enable two-way roads.", help="There are only a few directed roads between city pairs in the dataset, so enabling this option is generally recommended.")
    with col2:
        show_tooltips = st.toggle("Show intermediate node tooltips", value=False)

# ---------- Load graph (cached) ---------
@st.cache_data(show_spinner=False)
def load_graph_data(undirected_flag: bool):
    nodes, adj = load_graph(undirected=undirected_flag)
    ids = list(nodes.keys())
    labels = {node_id: f"{nodes[node_id]['name']} ({node_id})" for node_id in ids}
    return nodes, adj, ids, labels

nodes, adj, ids, labels = load_graph_data(undirected)


# ---------------- Source, Target, and Mode Selection ----------------
with st.container(border=True):
    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        src_id = st.selectbox("Source", options=ids, format_func=lambda x: labels[x], index=0)
    with c2:
        dst_id = st.selectbox("Target", options=ids, format_func=lambda x: labels[x], index=1)
    with c3:
        mode = st.radio("Mode of shortest path", ["Distance (km)", "Travel time (min)"], index=0, horizontal=True)
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

# ----------------------------- Edge & Node Count ----------------------------- #
def edge_count(path_ids) -> int:
    return max(0, len(path_ids) - 1)

def node_count(path_ids) -> int:
    return len(path_ids)

def algorithm_step_count(result: dict) -> int | None:
    if "relaxations_done" in result:
        return result["relaxations_done"]
    return None



# ---------------- Run Algorithms and Show Maps ----------------
if go:
    nodes_used, results, maps = run_all(
        start=src_id,
        goal=dst_id,
        weight_key=weight_key,
        undirected=undirected,
        return_maps=True,
        show_tooltips=show_tooltips,
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
                st.divider()
                
                st.markdown("#### Algorithm details")
                # Algorithm runtime (ms)
                st.markdown(f"**Computation time:** `{result['runtime_sec'] * 1000:.1f} ms`")

                # NEW: Step count + (optional) breakdown
                steps = algorithm_step_count(result)
                if steps is not None:
                    st.markdown(f"**Step count:** `{steps}`")

                # Display Steps
                has_step_metrics_bellman_ford = any(k in result for k in ("iterations", "relaxations_done", "edges_scanned"))
                if has_step_metrics_bellman_ford:
                    iters = result.get("iterations", "-")
                    relx  = result.get("relaxations_done", "-")
                    scans = result.get("edges_scanned", "-")
                    st.markdown(f"**Passes:** `{iters}`  | **Relaxations:** `{relx}`  | **Edges scanned:** `{scans}`")
                st.divider()

                # Display other details
                if result["path"]:
                    total_km  = total_distance_km(result["path"], adj)
                    total_min = total_time_min(result["path"], adj)

                    st.markdown("#### Route details")
                    st.markdown(f"**Total Distance:** `{total_km:.3f} km`")
                    st.markdown(f"**Total Time:** `{total_min:.2f} min`")
                    st.markdown(f"**Roads count:** `{edge_count(result['path'])}`")
                    st.markdown(f"**Cities count:** `{node_count(result['path'])}`")

                    # Stops (traveling city list)
                    stops = " → ".join(nodes_used[n]["name"] for n in result["path"])
                    st.markdown(f"**Stops:** {stops}")
                else:
                    st.markdown("**Total Distance:** `N/A`")
                    st.markdown("**Total Time:** `N/A`")
                    st.markdown("**Roads count:** `N/A`")
                    st.markdown("**Cities count:** `N/A`")
                    st.warning("No path found for this algorithm.")
                
else:
    st.info("Pick a Source and Destination, then click **Compute routes**.")




