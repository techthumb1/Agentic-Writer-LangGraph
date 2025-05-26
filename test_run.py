from langgraph_app.graph import graph

if __name__ == "__main__":
    initial_state = {}
    final_state = graph.invoke(initial_state)

    print("Finalized Output:")
    print(final_state["formatted_article"])
