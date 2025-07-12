from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional, Dict
import os
from graphviz import Source  # pip install graphviz

# Define state schema
class SalesState(TypedDict):
    data: Dict[str, float]
    result: Optional[Dict[str, float]]
    alerts: Optional[List[str]]
    recommendations: Optional[List[str]]

# Node definitions
def input_node(state: SalesState) -> SalesState:
    return state

def processing_node(state: SalesState) -> SalesState:
    today = state["data"]
    yesterday = today.get("yesterday", {})
    sales = today.get("sales", 0)
    cost = today.get("cost", 0)
    customers = today.get("customers", 1)
    profit = sales - cost
    cac = cost / max(customers, 1)

    result = {"profit": profit, "CAC": cac}
    alerts = []
    if yesterday:
        if yesterday.get("CAC", 0) < cac:
            alerts.append("⚠️ CAC has increased compared to yesterday.")
        if yesterday.get("sales", 0) < sales:
            alerts.append("✅ Sales have increased compared to yesterday.")
    return {**state, "result": result, "alerts": alerts}

def recommendation_node(state: SalesState) -> SalesState:
    recs = []
    if state["result"]["profit"] < 0:
        recs.append("🔴 You are running at a loss. Consider reducing costs.")
    else:
        recs.append("🟢 You are making a profit.")
    alerts = state.get("alerts", [])
    if "⚠️ CAC has increased compared to yesterday." in alerts:
        recs.append("📉 Consider improving your acquisition channels.")
    if "✅ Sales have increased compared to yesterday." in alerts:
        recs.append("📈 You may increase the marketing budget to leverage momentum.")
    return {**state, "recommendations": recs}

# Build and compile the graph
builder = StateGraph(SalesState)
builder.add_node("input_node", input_node)
builder.add_node("processing_node", processing_node)
builder.add_node("recommendation_node", recommendation_node)
builder.set_entry_point("input_node")
builder.add_edge("input_node", "processing_node")
builder.add_edge("processing_node", "recommendation_node")
builder.add_edge("recommendation_node", END)

graph = builder.compile()

# ASCII visualization
print("\n--- Graph structure (ASCII) ---")
print(graph.get_graph().draw_ascii())

# ✅ Export PNG using built-in method
try:
    png_bytes = graph.get_graph().draw_png()
    with open("sales_graph.png", "wb") as f:
        f.write(png_bytes)
    print("✅ Graph exported to sales_graph.png")
except Exception as e:
    print("❌ Skipping image export due to error:", e)

# Run sample
sample_input = {
    "data": {
        "sales": 12000,
        "cost": 4000,
        "customers": 100,
        "yesterday": {"sales": 10000, "cost": 3500, "CAC": 35.0}
    }
}
output = graph.invoke(sample_input)
print("\n🔍 Final Output:\n", output)
