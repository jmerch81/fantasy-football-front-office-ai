import streamlit as st
from src.executives.general_manager import GeneralManager

st.set_page_config(
    page_title="General Manager Office",
    page_icon="👔",
    layout="wide"
)

gm = GeneralManager()
recommendation = gm.make_recommendation()

st.title("👔 General Manager Office")
st.subheader("Alex Morgan")

st.markdown(f"> *{gm.signature_phrase}*")

col1, col2, col3 = st.columns(3)

col1.metric("Status", "Active")
col2.metric("Primary Focus", "Roster Construction")
col3.metric("Confidence", f"{recommendation.confidence:.0%}")

st.divider()

st.header("🎯 Mission")
st.write(gm.mission)

st.header("🧠 Executive Personality")
st.write(", ".join(gm.personality))

st.header("📋 Current Recommendation")
st.success(recommendation.recommendation)

st.header("📊 Confidence")
st.progress(recommendation.confidence)

st.header("✅ Supporting Evidence")
for item in recommendation.evidence:
    st.write(f"- {item}")

st.header("⚠️ Risk Assessment")
for risk in recommendation.risks:
    st.write(f"- {risk}")

st.header("📌 Current Priorities")
st.write("- Add running back depth")
st.write("- Monitor waiver wire")
st.write("- Preserve roster flexibility")
st.write("- Avoid overpaying in trades")

st.header("🏆 Long-Term Strategy")
st.write(
    "Build a championship-caliber roster by balancing short-term weekly needs "
    "with long-term roster value, depth, flexibility, and upside."
)