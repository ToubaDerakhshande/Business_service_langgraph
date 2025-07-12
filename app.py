import streamlit as st
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional, Dict
import graphviz
import tempfile
import base64
import ast

# تعریف ساختار حالت (State)
class SalesState(TypedDict):
    data: Dict[str, float]
    result: Optional[Dict[str, float]]
    alerts: Optional[List[str]]
    recommendations: Optional[List[str]]

# نود اول: ورودی
def input_node(state: SalesState) -> SalesState:
    return state

# نود پردازش
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

# نود پیشنهاد
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

# ساخت گراف با StateGraph (قبل از کامپایل)
builder = StateGraph(SalesState)
builder.add_node("input_node", input_node)
builder.add_node("processing_node", processing_node)
builder.add_node("recommendation_node", recommendation_node)
builder.set_entry_point("input_node")
builder.add_edge("input_node", "processing_node")
builder.add_edge("processing_node", "recommendation_node")
builder.add_edge("recommendation_node", END)

# کامپایل گراف
graph = builder.compile()

# تابع ساختن dot از builder (سازگار با edges به صورت set از tuple)
def build_dot_from_graph(state_graph):
    dot = "digraph G {\n"
    for node_name in state_graph.nodes.keys():
        dot += f'    "{node_name}";\n'
    for source, dest in state_graph.edges:
        dot += f'    "{source}" -> "{dest}";\n'
    dot += "}"
    return dot

# --- رابط گرافیکی Streamlit ---
st.set_page_config(page_title="LangGraph Studio (Local)", layout="wide")
st.title("🧠 LangGraph Test Studio - Sales Graph")

st.markdown("وارد کردن ورودی JSON:")

sample_input = {
    "data": {
        "sales": 12000,
        "cost": 4000,
        "customers": 100,
        "yesterday": {
            "sales": 10000,
            "cost": 3500,
            "CAC": 35.0
        }
    }
}

user_input = st.text_area("ورودی (JSON):", value=str(sample_input), height=200)

run_button = st.button("اجرای گراف")

if run_button:
    try:
        input_data = ast.literal_eval(user_input)

        # اجرای گراف
        result = graph.invoke(input_data)

        # نمایش خروجی
        st.subheader("🔍 خروجی نهایی:")
        st.json(result)

        # رسم گراف در Streamlit با استفاده از builder
        st.subheader("📊 ساختار گراف:")
        dot = build_dot_from_graph(builder)
        st.graphviz_chart(dot)

        # --- ذخیره گراف به صورت تصویر PNG و لینک دانلود ---
        st.subheader("📥 دانلود گراف به صورت تصویر PNG:")

        src = graphviz.Source(dot)
        with tempfile.TemporaryDirectory() as tmpdirname:
            png_path = f"{tmpdirname}/graph"
            src.render(filename=png_path, format="png", cleanup=True)

            # خواندن فایل PNG برای ایجاد لینک دانلود
            with open(f"{png_path}.png", "rb") as f:
                img_bytes = f.read()
                b64 = base64.b64encode(img_bytes).decode()
                href = f'<a href="data:image/png;base64,{b64}" download="graph.png">⬇️ دانلود گراف (PNG)</a>'
                st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ خطا در اجرای گراف: {e}")
