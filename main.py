from dotenv import load_dotenv
load_dotenv()

from graph.graph import build_graph
from graph.schemas.state import State
import os

def main():
    # List all .md files in input/
    input_dir = "input"
    files = [f for f in os.listdir(input_dir) if f.endswith(".md")]
    if not files:
        print("No .md files found in input/ directory.")
        return
    print("Select a PRD file to process:")
    for idx, fname in enumerate(files, 1):
        print(f"  {idx}. {fname}")
    while True:
        try:
            choice = int(input("Enter number: "))
            if 1 <= choice <= len(files):
                break
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a valid number.")
    selected_file = os.path.join(input_dir, files[choice - 1])
    print(f"Selected: {selected_file}")
    state = State(input_path=selected_file)
    graph = build_graph()
    result = graph.invoke(state)
    print("\nDAG complete.")
    if getattr(result, 'chunks', None):
        print("Number of chunks:", len(result.chunks))
    if getattr(result, 'strategic_context', None):
        print("Strategic context extracted.")

if __name__ == "__main__":
    main() 