from langgraph.graph import StateGraph, END, START
from graph.nodes.prechunker import prechunker
from graph.nodes.chunker import chunker
from graph.nodes.strategic_overview import strategic_overview
from graph.nodes.component_router import component_router, router_conditional
from graph.nodes.canvas_app_agent import canvas_app_agent
from graph.nodes.power_automate_agent import power_automate_agent
from graph.schemas.state import State

def build_graph():
    graph = StateGraph(state_schema=State)
    graph.add_node("prechunker", prechunker)
    graph.add_node("chunker", chunker)
    graph.add_node("strategic_overview", strategic_overview)
    graph.add_node("component_router", component_router)
    graph.add_node("canvas_app_agent", canvas_app_agent)
    graph.add_node("power_automate_agent", power_automate_agent)
    # Define edges
    graph.add_edge(START, "prechunker")
    graph.add_edge("prechunker", "chunker")
    graph.add_edge("chunker", "strategic_overview")
    graph.add_edge("strategic_overview", "component_router")
    # Conditional edge: router decides next node (returns string node names)
    graph.add_conditional_edges("component_router", router_conditional)
    # After agent, return to router for next component (if any)
    graph.add_edge("canvas_app_agent", "component_router")
    graph.add_edge("power_automate_agent", "component_router")
    return graph.compile() 