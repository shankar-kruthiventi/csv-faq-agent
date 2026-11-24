import sys
from getpass import getpass

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

from src import loader

MODEL_NAME = "openai/gpt-6-luna"
BASE_URL = "https://openrouter.ai/api/v1"

# State used only by the terminal (CLI) flow. The Streamlit UI passes everything explicitly.
dataframes = []
loaded_names = []
api_key = ''
system_prompt = ''


def build_system_prompt(names, dfs):
    """Build the system prompt from the datasets that are actually loaded."""
    dataset_lines = "\n".join(
        f"    - {name}: columns = {', '.join(map(str, df.columns))}"
        for name, df in zip(names, dfs)
    )
    return f"""
    You are a smart data assistant capable of reading multiple CSV files.
    You have access to {len(dfs)} dataset(s):
{dataset_lines}

    Rules:
    - Answer ONLY from the data in these DataFrames. Do NOT answer from general knowledge.
    - Determine which DataFrame is most relevant to the question.
    - Do NOT assume anything. If the question is ambiguous (e.g. several rows or datasets could apply,
      or a needed detail such as plan, card type or department is missing), ask the user a short
      clarifying question instead of guessing.
    - If the data does not contain the answer, say so and ask the user how they would like to proceed.
    - Answer in plain English.
    """


def build_query(question, history=None, prompt=None, max_turns=10):
    """Combine the system prompt, recent conversation and the new question.

    `history` is a list of {"role": "user"|"assistant", "content": str}. It lets the agent
    understand the user's reply to one of its clarifying questions.
    """
    prompt = prompt if prompt is not None else system_prompt
    convo = ""
    if history:
        lines = [
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in history[-max_turns * 2:]
        ]
        convo = "\n\nConversation so far:\n" + "\n".join(lines)
    return f"{prompt}{convo}\n\nQuestion: {question}"


def create_agent(key=None, dfs=None):
    """Create the pandas agent. Falls back to the module-level state used by the CLI."""
    key = key or api_key
    dfs = dfs if dfs is not None else dataframes
    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=key,
        base_url=BASE_URL,
    )
    return create_pandas_dataframe_agent(
        llm,
        dfs,
        verbose=True,
        agent_type="openai-functions",
        allow_dangerous_code=True,
    )


# ---------------------------------------------------------------------------
# Terminal (CLI) flow, used by app.py
# ---------------------------------------------------------------------------
def get_api_key():
    print("ENTER YOUR OPENAI API KEY BELOW:")
    return getpass()


def form_dataframes():
    global api_key, system_prompt
    api_key = get_api_key()
    if not api_key:
        print("ERROR: No API key provided. Exiting.")
        sys.exit()
    print("API Key received. Proceeding to load CSV files...\n")

    try:
        for filename in loader.files_to_download.keys():
            df = pd.read_csv(filename)
            dataframes.append(df)
            loaded_names.append(filename)
            print(f"SUCCESS: Loaded '{filename}' ({len(df)} rows)")
    except Exception as e:
        print(f"\nERROR loading files: {e}")
        sys.exit()

    system_prompt = build_system_prompt(loaded_names, dataframes)
