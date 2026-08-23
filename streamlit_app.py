"""Tiny Streamlit starter — deploy on Streamlit Community Cloud."""
import streamlit as st

st.set_page_config(page_title="Sean’s Python starter", page_icon="🛠️", layout="centered")
st.title("Sean’s Python publishing starter")
st.write(
    "If you can open this link, Streamlit Community Cloud is working. "
    "Skyler can ship real Python apps here — calculators, sims, file tools, dashboards."
)

name = st.text_input("Your name", value="Sean")
mode = st.radio("Mode", ["chill", "builder", "chaos"], horizontal=True)

if st.button("Say hi"):
    st.success(f"Hey {name.strip() or 'friend'} — Python apps are live. Vibe: {mode}.")

st.caption("Repo: github.com/seanholt111/streamlit-starter")
