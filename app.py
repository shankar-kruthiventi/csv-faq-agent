from src import loader, csv_agent, chat_loop

loader.get_files()  # Download CSV files if they don't exist
csv_agent.form_dataframes()  # Load CSV files into DataFrames
agent = csv_agent.create_agent()  # Create the AI agent
chat_loop.start_chat(agent)  # Start the chat loop with the agent