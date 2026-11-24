from src import csv_agent


def start_chat(agent):
    print("\nAI Agent is ready! You can ask questions across ALL files.")
    print("Type 'exit' or 'quit' to stop conversation.\n")
    history = []

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        final_query = csv_agent.build_query(user_input, history)
        print("AI is thinking...")

        try:
            response = agent.invoke(final_query)
            answer = response['output']
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": answer})
            print(f"AI: {answer}\n" + "-"*30)
        except Exception as e:
            print(f"An error occurred: {e}")
