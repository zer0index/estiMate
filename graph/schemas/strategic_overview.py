"""
Pydantic schemas for the Strategic Overview node.
"""

from typing import List, Optional, Literal, Union, Dict
from pydantic import BaseModel

class AppScreen(BaseModel):
    screen_name: str
    screen_type: Literal["CanvasApp", "ModelDrivenApp", "PowerPages", "PowerBI", "Other"]
    screen_details: str
    features: Optional[Dict[str, str]] = None

class AppComponent(BaseModel):
    app_name: str
    app_type: Literal["CanvasApp", "ModelDrivenApp", "PowerPages", "PowerBI", "Other"]
    app_details: str
    app_screens: List[AppScreen]

class FlowAction(BaseModel):
    action_name: str
    action_type: Literal["PowerAutomate", "Other"]
    action_details: str
    features: Optional[Dict[str, str]] = None

class FlowComponent(BaseModel):
    flow_name: str
    flow_type: Literal["PowerAutomate", "Other"]
    flow_details: str
    flow_actions: List[FlowAction]

MVPComponent = Union[AppComponent, FlowComponent]

class PostMVPModule(BaseModel):
    module_name: str
    extension_type: Literal["AppScreen", "Dashboard", "ModelDrivenApp", "PowerAutomate", "Other"]
    extends_component: str  # e.g., "Device Order App" or "Approval Workflow"
    details: str
    recommendation: str  # e.g., "Best fit: add as a screen to Device Order App"

class UserRole(BaseModel):
    role_name: str
    permissions: List[str]

class SystemRole(BaseModel):
    role_name: str
    technical_scope: List[str]

class StrategicContext(BaseModel):
    purpose: str
    business_value: List[str]
    mvp_components: List[MVPComponent]
    post_mvp_modules: Optional[List[PostMVPModule]] = None
    user_roles: List[UserRole]
    system_roles: List[SystemRole]
    constraints: List[str]
    integration_points: List[str]
    notes: Optional[str] = None 