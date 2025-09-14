from __future__ import annotations

import streamlit as st, pathlib
from streamlit.components.v1 import html
import pandas as pd

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
    if "explored" in result:    # A*
        return result["explored"]
    if "iterations" in result:   # Bellman–Ford
        return result["iterations"]
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
                    relx  = result.get("relaxations_done", "-")
                    scans = result.get("edges_scanned", "-")
                    st.markdown(f"**Relaxations:** `{relx}`")
                    st.markdown(f"**Edges scanning count:** `{scans}`")
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
                    st.markdown(f"##### Stops")
                    st.markdown(f" {stops}")
                else:
                    st.markdown("**Total Distance:** `N/A`")
                    st.markdown("**Total Time:** `N/A`")
                    st.markdown("**Roads count:** `N/A`")
                    st.markdown("**Cities count:** `N/A`")
                    st.warning("No path found for this algorithm.")
                
else:
    st.info("Pick a Source and Destination, then click **Compute routes**.")


st.divider()
# ---------------- Possible Pairs (Directed & Undirected) ----------------
@st.cache_data(show_spinner=False)
def load_pairs_df():
    path = pathlib.Path("data/diff_paths_directed_vs_undirected.csv")
    if not path.exists():
        raise FileNotFoundError(f"Could not find {path}. Please ensure the CSV file is in the 'data' directory.")
    df = pd.read_csv(path)
    keep_cols = [c for c in ["source_name", "target_name"] if c in df.columns]
    if not keep_cols:
        raise ValueError("CSV must include 'source_name' and 'target_name' columns.")
    return df[keep_cols].dropna()

def render_pairs_panel():
    if "pairs_offset" not in st.session_state:
        st.session_state.pairs_offset = 0
    if "pairs_limit" not in st.session_state:
        st.session_state.pairs_limit = 200

    try:
        df_pairs = load_pairs_df()
    except Exception as e:
        st.error(str(e))
        return

    q = st.text_input("Search source or target…", key="pairs_q")
    limit = st.number_input("Rows per page", 50, 1000, st.session_state.pairs_limit, step=50, key="pairs_limit_num")
    st.session_state.pairs_limit = int(limit)

    cur = df_pairs
    if q:
        ql = q.lower()
        src_ok = "source_name" in cur.columns
        tgt_ok = "target_name" in cur.columns
        if src_ok and tgt_ok:
            cur = cur[cur["source_name"].str.lower().str.contains(ql) | cur["target_name"].str.lower().str.contains(ql)]
        elif src_ok:
            cur = cur[cur["source_name"].str.lower().str.contains(ql)]
        elif tgt_ok:
            cur = cur[cur["target_name"].str.lower().str.contains(ql)]

    total = len(cur)
    offset = min(st.session_state.pairs_offset, max(0, max(0, total - 1)))

    cols = st.columns([1,1,4])
    with cols[0]:
        if st.button("Search / Refresh", key="pairs_refresh"):
            st.session_state.pairs_offset = 0
            offset = 0

    start = offset
    end = min(offset + st.session_state.pairs_limit, total)
    page = cur.iloc[start:end]

    st.dataframe(page, width='stretch', height=420)

    c1, c2, c3, c4 = st.columns([2,1,1,2])
    with c1:
        st.caption(f"Showing {start + 1 if total else 0}–{end} of {total:,}")
    with c2:
        if st.button("‹ Prev", disabled=start <= 0, key="pairs_prev"):
            st.session_state.pairs_offset = max(0, start - st.session_state.pairs_limit)
            st.rerun()
    with c3:
        if st.button("Next ›", disabled=end >= total, key="pairs_next"):
            st.session_state.pairs_offset = start + st.session_state.pairs_limit
            st.rerun()
    with c4:
        if st.button("Close", key="pairs_close"):
            st.session_state.show_pairs = False
            st.rerun()

with st.container(border=True):
    st.subheader("Tip: Explore Possible Paths (Directed & Undirected)")
    st.markdown("Shows city pairs where at least one path exists in both modes of directed and undirected road networks.")
    if st.button("View pairs", type="primary", key="pairs_open"):
        st.session_state.show_pairs = False if st.session_state.get("show_pairs") else True

    if st.session_state.get("show_pairs"):
        # Use a modal if this Streamlit version supports it; otherwise, fall back to an expander
        if hasattr(st, "modal"):
            with st.modal("City Pairs (source → target)", key="pairs_modal"):
                render_pairs_panel()
        else:
            with st.expander("City Pairs (source → target)", expanded=True):
                render_pairs_panel()





