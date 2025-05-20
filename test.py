from typing import Annotated, Literal
from typing_extensions import TypedDict
import random
from langgraph.graph import StateGraph, START, END

# Define the state schema
class State(TypedDict):
    # Using Annotated to specify how to combine values
    number: int
    message: str

# Node 1 - Starting node
def node1(state: State):
    print("Starting execution from Node 1")
    return {"message": "Node 1 executed"}

# Node 2 - Random number generator
def node2(state: State):
    number = random.randint(1, 3)
    print(f"Node 2 generated number: {number}")
    return {"number": number, "message": f"Generated number {number}"}

# Node 3 - Executes if number is 1
def node3(state: State):
    print("Executing Node 3 (number was 1)")
    return {"message": "Node 3 executed"}

# Node 4 - Executes if number is 2
def node4(state: State):
    print("Executing Node 4 (number was 2)")
    return {"message": "Node 4 executed"}

# Node 5 - Executes if number is 3
def node5(state: State):
    print("Executing Node 5 (number was 3)")
    return {"message": "Node 5 executed"}

# Define conditional routing based on the number
def route_based_on_number(state: State) -> Literal["node3", "node4", "node5", END]:
    number = state["number"]
    if number == 1:
        return "node3"
    elif number == 2:
        return "node4"
    else:
        return "node5"

# Create and configure the graph
def create_graph():
    # Initialize the graph with our state
    builder = StateGraph(State)
    
    # Add all nodes
    builder.add_node("node1", node1)
    builder.add_node("node2", node2)
    builder.add_node("node3", node3)
    builder.add_node("node4", node4)
    builder.add_node("node5", node5)
    
    # Add edges
    builder.add_edge(START, "node1")
    builder.add_edge("node1", "node2")
    
    # Add conditional edges from node2
    builder.add_conditional_edges("node2", route_based_on_number)
    
    # Add edges to END from terminal nodes
    builder.add_edge("node3", END)
    builder.add_edge("node4", END)
    builder.add_edge("node5", END)
    
    return builder.compile()

if __name__ == "__main__":
    # Create the graph
    graph = create_graph()
    
    print("\n--- New Run ---")
    result = graph.invoke({"number": 0, "message": ""})
    print("Final state:", result)
