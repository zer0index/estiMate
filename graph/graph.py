from langgraph.graph import StateGraph, END, START
from graph.nodes.prechunker import prechunker
from graph.nodes.chunker import chunker
from graph.nodes.strategic_overview import strategic_overview
from graph.nodes.feature_extractor import feature_extractor
from graph.schemas.state import State

def build_graph():
    graph = StateGraph(state_schema=State)
    graph.add_node("prechunker", prechunker)
    graph.add_node("chunker", chunker)
    graph.add_node("strategic_overview", strategic_overview)
    graph.add_node("feature_extractor", feature_extractor)
    # Define edges
    graph.add_edge(START, "prechunker")
    graph.add_edge("prechunker", "chunker")
    graph.add_edge("chunker", "strategic_overview")
    graph.add_edge("strategic_overview", "feature_extractor")
    graph.add_edge("feature_extractor", END)
    return graph.compile() 