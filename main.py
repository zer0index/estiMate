from dotenv import load_dotenv
load_dotenv()

from graph.graph import build_graph
from graph.schemas.state import State

def main():
    state = State()
    graph = build_graph()
    result = graph.invoke(state)
    print("\nDAG complete.")
    if getattr(result, 'chunks', None):
        print("Number of chunks:", len(result.chunks))
    if getattr(result, 'strategic_context', None):
        print("Strategic context extracted.")

if __name__ == "__main__":
    main() 