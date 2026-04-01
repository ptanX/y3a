"""
Plugins Router – Quản lý Plugin Registry.
GET /api/plugins              → Danh sách plugin đang bật
GET /api/plugins/{plugin_id}  → Chi tiết một plugin
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from api.routers.auth import get_current_user
from plugin_registry.plugin_loader import plugin_loader

router = APIRouter()


# ── Models ────────────────────────────────────────────────────────────────────
class PluginInfo(BaseModel):
    id: str
    name: str
    version: str
    description: str
    icon: str
    tags: List[str]
    requires_services: List[str]
    api_endpoint: Optional[str] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.get("", response_model=List[PluginInfo])
def list_plugins(current_user: dict = Depends(get_current_user)):
    """
    Trả về danh sách plugin đang được kích hoạt,
    lọc theo permission của user hiện tại.
    """
    from frontend.role_controller import ROLE_PERMISSIONS
    plugins = plugin_loader.get_plugins_by_permission(
        role=current_user["role"],
        role_permissions=ROLE_PERMISSIONS,
    )
    return [
        PluginInfo(
            id=p.id,
            name=p.name,
            version=p.version,
            description=p.description,
            icon=p.icon,
            tags=p.tags,
            requires_services=p.requires_services,
            api_endpoint=p.api_endpoint,
        )
        for p in plugins
    ]


@router.get("/{plugin_id}", response_model=PluginInfo)
def get_plugin(plugin_id: str, current_user: dict = Depends(get_current_user)):
    """Lấy chi tiết một plugin theo ID."""
    plugin = plugin_loader.get(plugin_id)
    if plugin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_id}' không tồn tại hoặc chưa được kích hoạt.",
        )
    return PluginInfo(
        id=plugin.id,
        name=plugin.name,
        version=plugin.version,
        description=plugin.description,
        icon=plugin.icon,
        tags=plugin.tags,
        requires_services=plugin.requires_services,
        api_endpoint=plugin.api_endpoint,
    )
