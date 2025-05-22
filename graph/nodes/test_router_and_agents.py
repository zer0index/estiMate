class DummyComponent:
    def __init__(self, app_type=None, flow_type=None, name=""):
        self.app_type = app_type
        self.flow_type = flow_type
        self.name = name
    def __repr__(self):
        return f"<Component name={self.name} app_type={self.app_type} flow_type={self.flow_type}>"

class DummyPowerPagesComponent(DummyComponent):
    def __init__(self, app_name, app_details, app_screens, processed=False):
        super().__init__(app_type="PowerPages", name=app_name)
        self.app_name = app_name
        self.app_type = "PowerPages"
        self.app_details = app_details
        self.app_screens = app_screens
        self.processed = processed

class DummyStrategicContext:
    def __init__(self, mvp_components):
        self.mvp_components = mvp_components

class DummyState:
    def __init__(self, strategic_context):
        self.strategic_context = strategic_context

# Create test components
components = [
    DummyComponent(app_type="CanvasApp", name="App1"),
    DummyComponent(flow_type="PowerAutomate", name="Flow1"),
    DummyPowerPagesComponent(
        app_name="Pages1",
        app_details="A Power Pages portal for suppliers.",
        app_screens=[],
        processed=False
    ),
    DummyComponent(app_type="UnknownType", name="Unknown1"),
]

state = DummyState(DummyStrategicContext(components))

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from graph.nodes.component_router import component_router
from graph.nodes.canvas_app_agent import canvas_app_agent
from graph.nodes.power_automate_agent import power_automate_agent
from graph.nodes.power_pages_agent import power_pages_agent

current_state = state
while True:
    router_output = component_router(current_state)
    next_node = router_output["next"]
    if next_node == "END":
        print("Reached END of routing.")
        break
    if next_node == "canvas_app_agent":
        current_state = canvas_app_agent(current_state)
    elif next_node == "power_automate_agent":
        current_state = power_automate_agent(current_state)
    elif next_node == "power_pages_agent":
        current_state = power_pages_agent(current_state)
    else:
        print(f"Unknown next node: {next_node}")
        break