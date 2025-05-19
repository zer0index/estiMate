"""
Pydantic schemas for the Strategic Overview node.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel

class Component(BaseModel):
    name: str
    type: Literal["CanvasApp", "ModelDrivenApp", "PowerAutomate", "Dataverse", "PowerPages", "CustomConnector", "Other"]
    details: Optional[str] = None

class UserRole(BaseModel):
    role_name: str
    permissions: List[str]

class SystemRole(BaseModel):
    role_name: str
    technical_scope: List[str]

class StrategicContext(BaseModel):
    purpose: str
    business_value: List[str]
    mvp_components: List[Component]
    post_mvp_modules: List[Component]
    user_roles: List[UserRole]
    system_roles: List[SystemRole]
    constraints: List[str]
    integration_points: List[str]
    notes: Optional[str] = None 