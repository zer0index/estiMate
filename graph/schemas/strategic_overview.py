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
    processed: bool = False

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
    processed: bool = False
    features: Optional[Dict[str, str]] = None
    actions: Optional[Dict[str, str]] = None
    connectors: Optional[Dict[str, str]] = None
    trigger: Optional[str] = None

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

class TableField(BaseModel):
    name: str
    type: str
    description: Optional[str] = None

class TableModel(BaseModel):
    table_name: str
    fields: List[TableField]
    primary_key: Optional[str] = None
    foreign_keys: Optional[List[str]] = None
    description: Optional[str] = None

class DatabaseModel(BaseModel):
    tables: List[TableModel]
    notes: Optional[str] = None

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
    database_model: Optional[DatabaseModel] = None 