"""
Plugin Loader – Engine tự động nhận diện, xác thực và nạp plugin.

Cách hoạt động:
1. Đọc plugin_registry/registry.json để biết plugin nào được kích hoạt.
2. Với mỗi plugin enabled, đọc manifest.json bên trong thư mục plugin đó.
3. Cung cấp danh sách plugin đã nạp để Streamlit Frontend render menu động.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Đường dẫn gốc của project
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
PLUGINS_DIR = PROJECT_ROOT / "plugins"
REGISTRY_FILE = PROJECT_ROOT / "plugin_registry" / "registry.json"


@dataclass
class PluginManifest:
    """Thông tin đầy đủ của một Plugin sau khi được nạp từ manifest.json."""
    id: str
    name: str
    version: str
    description: str
    icon: str
    nav_label: str
    nav_page: str              # Đường dẫn tới file Streamlit page
    required_permission: str   # Permission key trong ROLE_PERMISSIONS
    requires_services: list    # Danh sách microservice cần thiết
    api_endpoint: Optional[str] = None
    enabled: bool = True
    tags: list = field(default_factory=list)


class PluginLoader:
    """
    Singleton loader quản lý vòng đời của tất cả plugin.
    Gọi PluginLoader() để lấy instance duy nhất.
    """
    _instance = None
    _plugins: dict[str, PluginManifest] = {}
    _loaded: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_all(self) -> list[PluginManifest]:
        """
        Nạp toàn bộ plugin từ registry.json.
        Chỉ thực hiện một lần, kết quả được cache.
        """
        if self._loaded:
            return list(self._plugins.values())

        if not REGISTRY_FILE.exists():
            print(f"[PluginLoader] Không tìm thấy registry tại {REGISTRY_FILE}")
            return []

        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            registry = json.load(f)

        for entry in registry.get("plugins", []):
            plugin_id = entry.get("id")
            enabled = entry.get("enabled", False)

            if not enabled:
                print(f"[PluginLoader] Plugin '{plugin_id}' đang TẮT, bỏ qua.")
                continue

            manifest_path = PLUGINS_DIR / plugin_id / "manifest.json"
            if not manifest_path.exists():
                print(f"[PluginLoader] ⚠️  Không tìm thấy manifest cho '{plugin_id}'")
                continue

            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                plugin = PluginManifest(
                    id=data["id"],
                    name=data["name"],
                    version=data.get("version", "1.0.0"),
                    description=data.get("description", ""),
                    icon=data.get("icon", "🧩"),
                    nav_label=data.get("nav_label", data["name"]),
                    nav_page=data["nav_page"],
                    required_permission=data.get("required_permission", plugin_id),
                    requires_services=data.get("requires_services", []),
                    api_endpoint=data.get("api_endpoint"),
                    enabled=True,
                    tags=data.get("tags", []),
                )
                self._plugins[plugin_id] = plugin
                print(f"[PluginLoader] ✅ Đã nạp plugin: {plugin.icon} {plugin.name} v{plugin.version}")

            except (json.JSONDecodeError, KeyError) as e:
                print(f"[PluginLoader] ❌ Lỗi nạp manifest '{plugin_id}': {e}")

        self._loaded = True
        return list(self._plugins.values())

    def get(self, plugin_id: str) -> Optional[PluginManifest]:
        """Lấy thông tin plugin theo ID."""
        if not self._loaded:
            self.load_all()
        return self._plugins.get(plugin_id)

    def get_enabled_plugins(self) -> list[PluginManifest]:
        """Lấy danh sách plugin đang được kích hoạt."""
        if not self._loaded:
            self.load_all()
        return [p for p in self._plugins.values() if p.enabled]

    def get_plugins_by_permission(self, role: str, role_permissions: dict) -> list[PluginManifest]:
        """
        Lọc plugin theo quyền của user hiện tại.
        Tích hợp với ROLE_PERMISSIONS trong role_controller.py.
        """
        enabled = self.get_enabled_plugins()
        user_permissions = role_permissions.get(role, [])
        return [p for p in enabled if p.required_permission in user_permissions]

    def reload(self):
        """Buộc nạp lại toàn bộ plugin (dùng khi admin thêm/xóa plugin runtime)."""
        self._plugins.clear()
        self._loaded = False
        return self.load_all()


# Singleton instance dùng trong toàn project
plugin_loader = PluginLoader()
