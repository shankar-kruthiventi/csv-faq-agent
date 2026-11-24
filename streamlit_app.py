import pandas as pd
import streamlit as st

from src import csv_agent, loader

st.set_page_config(page_title="CSV FAQ Agent", page_icon="📄")
st.title("📄 CSV FAQ Agent")

DEFAULTS = {
    "step": 1,
    "dataframes": {},   # filename -> DataFrame
    "uploader_key": 0,  # bumped to clear the uploader widget
    "api_key": "",
    "agent": None,
    "system_prompt": "",
    "messages": [],
}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

ss = st.session_state
STEPS = ["Add CSV files", "OpenAI API key", "Chat"]


def go(step):
    ss.step = step
    st.rerun()


def reset_chat():
    ss.agent = None
    ss.messages = []


# ------------------------------------------------------------ Step indicator
cols = st.columns(len(STEPS))
for i, (col, label) in enumerate(zip(cols, STEPS), start=1):
    if i < ss.step:
        col.markdown(f"✅ ~~{i}. {label}~~")
    elif i == ss.step:
        col.markdown(f"**➡️ {i}. {label}**")
    else:
        col.markdown(f"<span style='opacity:.5'>{i}. {label}</span>", unsafe_allow_html=True)
st.progress((ss.step - 1) / (len(STEPS) - 1))
st.divider()

# ---------------------------------------------------------------- Step 1: CSVs
if ss.step == 1:
    st.header("Step 1: Add your CSV files")
    uploaded = st.file_uploader(
        "Upload one or more CSV files", type="csv", accept_multiple_files=True,
        key=f"uploader_{ss.uploader_key}",
    )

    if st.button("Load sample datasets (downloads from Google Drive)"):
        try:
            with st.spinner("Downloading sample files..."):
                loader.get_files()
                for name in loader.files_to_download:
                    ss.dataframes[name] = pd.read_csv(name)
            reset_chat()
            st.success("Sample datasets loaded.")
        except Exception as e:
            st.error(f"Could not load sample datasets: {e}")

    for f in uploaded or []:
        try:
            f.seek(0)
            df = pd.read_csv(f)
        except Exception as e:
            st.error(f"Could not read '{f.name}': {e}")
            continue
        if f.name not in ss.dataframes or not ss.dataframes[f.name].equals(df):
            ss.dataframes[f.name] = df
            reset_chat()

    if ss.dataframes:
        st.write(f"**{len(ss.dataframes)} file(s) loaded:**")
        for name, df in list(ss.dataframes.items()):
            c1, c2 = st.columns([5, 1])
            c1.write(f"`{name}`: {len(df)} rows, {len(df.columns)} columns")
            if c2.button("Remove", key=f"rm_{name}"):
                del ss.dataframes[name]
                ss.uploader_key += 1  # otherwise the uploader would re-add the file
                reset_chat()
                st.rerun()
    else:
        st.info("Upload at least one CSV file (or load the sample datasets) to continue.")

    if st.button("Next ➡️", type="primary", disabled=not ss.dataframes):
        go(2)

# -------------------------------------------------------------- Step 2: API key
elif ss.step == 2:
    st.header("Step 2: Enter your OpenAI API key")
    key_input = st.text_input("OpenAI API key", type="password", value=ss.api_key).strip()
    if key_input != ss.api_key:
        ss.api_key = key_input
        reset_chat()

    back, nxt, _ = st.columns([1, 1.3, 4])
    if back.button("⬅️ Back"):
        go(1)
    if nxt.button("Start chat ➡️", type="primary", disabled=not ss.api_key):
        try:
            names = list(ss.dataframes.keys())
            dfs = list(ss.dataframes.values())
            ss.system_prompt = csv_agent.build_system_prompt(names, dfs)
            ss.agent = csv_agent.create_agent(ss.api_key, dfs)
        except Exception as e:
            st.error(f"Could not start the agent: {e}")
        else:
            go(3)
    if not ss.api_key:
        st.info("Enter your API key to continue.")

# ------------------------------------------------------------------ Step 3: Chat
else:
    if ss.agent is None:  # e.g. session state was cleared
        go(2)

    st.header("Step 3: Chat with your data")
    if st.button("⬅️ Back to settings"):
        reset_chat()
        go(2)

    for m in ss.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if question := st.chat_input("Ask a question about your CSV files"):
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    query = csv_agent.build_query(question, ss.messages, ss.system_prompt)
                    answer = ss.agent.invoke(query)["output"]
                except Exception as e:
                    answer = f"An error occurred: {e}"
            st.markdown(answer)
        ss.messages.append({"role": "user", "content": question})
        ss.messages.append({"role": "assistant", "content": answer})
