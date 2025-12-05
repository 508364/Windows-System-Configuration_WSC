"""Windows系统配置信息获取库"""

# 版本信息
__version__ = "0.1.0"

# 导入主要类
from .system import SystemInfo
from .hardware import HardwareInfo
from .configuration import ConfigurationInfo
from .software import SoftwareInfo
from .network import NetworkInfo
from .security import SecurityInfo

# 导入工具函数
from .utils import (
    format_bytes,
    format_timestamp,
    read_registry_value,
    get_registry_subkeys,
    get_registry_values,
    safe_int,
    safe_float
)

# 定义默认导出
default_system_info = SystemInfo()
default_hardware_info = HardwareInfo()
default_configuration_info = ConfigurationInfo()
default_software_info = SoftwareInfo()
default_network_info = NetworkInfo()
default_security_info = SecurityInfo()

# 导出便捷函数
def get_system_info():
    """获取系统基本信息"""
    return default_system_info.get_all_info()

def get_hardware_info():
    """获取硬件信息"""
    return default_hardware_info.get_all_hardware_info()

def get_configuration_info():
    """获取系统配置信息"""
    return default_configuration_info.get_all_configuration()

def get_software_info():
    """获取软件信息"""
    return default_software_info.get_all_software_info()

def get_network_info():
    """获取网络信息"""
    return default_network_info.get_all_network_info()

def get_security_info():
    """获取安全信息"""
    return default_security_info.get_all_security_info()

def get_all_info():
    """获取所有系统信息"""
    return {
        "system": get_system_info(),
        "hardware": get_hardware_info(),
        "configuration": get_configuration_info(),
        "software": get_software_info(),
        "network": get_network_info(),
        "security": get_security_info()
    }

def main():
    """WSC库的命令行入口点"""
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Windows System Configuration (WSC) v" + __version__)
        print("使用方法: wsc <命令>")
        print("可用命令:")
        print("  system      - 获取系统基本信息")
        print("  hardware    - 获取硬件信息")
        print("  configuration - 获取系统配置信息")
        print("  software    - 获取软件信息")
        print("  network     - 获取网络配置信息")
        print("  security    - 获取安全信息")
        print("  all         - 获取所有系统信息")
        print("  version     - 显示版本信息")
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "version":
        print("Windows System Configuration (WSC) v" + __version__)
    elif command == "system":
        print(json.dumps(get_system_info(), ensure_ascii=False, indent=2))
    elif command == "hardware":
        print(json.dumps(get_hardware_info(), ensure_ascii=False, indent=2))
    elif command == "configuration":
        print(json.dumps(get_configuration_info(), ensure_ascii=False, indent=2))
    elif command == "software":
        print(json.dumps(get_software_info(), ensure_ascii=False, indent=2))
    elif command == "network":
        print(json.dumps(get_network_info(), ensure_ascii=False, indent=2))
    elif command == "security":
        print(json.dumps(get_security_info(), ensure_ascii=False, indent=2))
    elif command == "all":
        print(json.dumps(get_all_info(), ensure_ascii=False, indent=2))
    else:
        print(f"未知命令: {command}")
        print("使用 wsc --help 查看可用命令")
        sys.exit(1)

# 导出所有类和函数
__all__ = [
    # 版本信息
    "__version__",
    
    # 主要类
    "SystemInfo",
    "HardwareInfo",
    "ConfigurationInfo",
    "SoftwareInfo",
    "NetworkInfo",
    "SecurityInfo",
    
    # 便捷函数
    "get_system_info",
    "get_hardware_info",
    "get_configuration_info",
    "get_software_info",
    "get_network_info",
    "get_security_info",
    "get_all_info",
    
    # 工具函数
    "format_bytes",
    "format_timestamp",
    "read_registry_value",
    "get_registry_subkeys",
    "get_registry_values",
    "safe_int",
    "safe_float",
    
    # 入口函数
    "main"
]
