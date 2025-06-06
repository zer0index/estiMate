from langgraph.graph import StateGraph, END, START
from graph.nodes.prechunker import prechunker
from graph.nodes.chunker import chunker
from graph.nodes.strategic_overview import strategic_overview
from graph.nodes.component_router import component_router, router_conditional
from graph.nodes.canvas_app_agent import canvas_app_agent
from graph.nodes.power_automate_agent import power_automate_agent
from graph.nodes.database_node import database_node
from graph.nodes.model_driven_agent import model_driven_agent
from graph.nodes.powerbi_agent import powerbi_agent
from graph.nodes.merge_agent import merge_agent
from graph.nodes.estimation_agent import estimation_agent
from graph.nodes.extractor_agent import extractor_agent
from graph.nodes.power_pages_agent import power_pages_agent
from graph.schemas.state import State

def build_graph():
    graph = StateGraph(state_schema=State)
    graph.add_node("prechunker", prechunker)
    graph.add_node("chunker", chunker)
    graph.add_node("strategic_overview", strategic_overview)
    graph.add_node("component_router", component_router)
    graph.add_node("canvas_app_agent", canvas_app_agent)
    graph.add_node("power_automate_agent", power_automate_agent)
    graph.add_node("database_node", database_node)
    graph.add_node("model_driven_agent", model_driven_agent)
    graph.add_node("powerbi_agent", powerbi_agent)
    graph.add_node("merge_agent", merge_agent)
    graph.add_node("estimation_agent", estimation_agent)
    graph.add_node("extractor_agent", extractor_agent)
    graph.add_node("power_pages_agent", power_pages_agent)
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
    graph.add_edge("database_node", "merge_agent")
    graph.add_edge("model_driven_agent", "component_router")
    graph.add_edge("powerbi_agent", "component_router")
    graph.add_edge("power_pages_agent", "component_router")
    graph.add_edge("merge_agent", "estimation_agent")
    graph.add_edge("estimation_agent", "extractor_agent")
    graph.add_edge("extractor_agent", END)
    return graph.compile()