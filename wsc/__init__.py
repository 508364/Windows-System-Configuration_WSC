"""Windows系统配置信息获取库"""

# 版本信息
__version__ = "0.1.1"

# 导入主要类
from .system import SystemInfo
from .hardware import HardwareInfo
from .configuration import ConfigurationInfo
from .software import SoftwareInfo
from .network import NetworkInfo
from .security import SecurityInfo

# 导入多语言支持
from .i18n import _, set_language, get_supported_languages

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
    
    # 处理--lang选项
    lang_index = -1
    for i, arg in enumerate(sys.argv):
        if arg in ['--lang', '-l']:
            if i + 1 < len(sys.argv):
                lang_index = i
                break
    
    if lang_index != -1:
        # 设置语言
        lang_code = sys.argv[lang_index + 1]
        set_language(lang_code)
        # 移除语言选项，避免影响后续命令处理
        del sys.argv[lang_index:lang_index + 2]
    
    # 检查是否请求帮助
    if len(sys.argv) >= 2 and sys.argv[1] in ['--help', '-h']:
        print(_("Windows System Configuration (WSC) v") + __version__)
        print(_("使用方法: wsc <命令> [选项]"))
        print(_("可用命令:"))
        print(_("  system      - 获取系统基本信息"))
        print(_("  hardware    - 获取硬件信息"))
        print(_("  configuration - 获取系统配置信息"))
        print(_("  software    - 获取软件信息"))
        print(_("  network     - 获取网络配置信息"))
        print(_("  security    - 获取安全信息"))
        print(_("  all         - 获取所有系统信息"))
        print(_("  version     - 显示版本信息"))
        print(_("\n可用选项:"))
        print(_("  system <选项>:"))
        print(_("    basic      - 只显示基本系统信息"))
        print(_("    os         - 只显示操作系统详细信息"))
        print(_("  hardware <选项>:"))
        print(_("    cpu        - 只显示CPU信息"))
        print(_("    memory     - 只显示内存信息"))
        print(_("    disks      - 只显示磁盘信息"))
        print(_("    gpu        - 只显示GPU信息"))
        print(_("    motherboard - 只显示主板信息"))
        print(_("  network <选项>:"))
        print(_("    adapters   - 只显示传统网络适配器信息"))
        print(_("    nic        - 只显示优化的网卡信息（推荐）"))
        print(_("    ip         - 只显示IP地址信息"))
        print(_("    stats      - 只显示网络统计信息"))
        print(_("    connections - 只显示网络连接信息"))
        print(_("  security <选项>:"))
        print(_("    users      - 只显示用户账户信息"))
        print(_("    groups     - 只显示用户组信息"))
        print(_("    current    - 只显示当前用户信息"))
        print(_("    sid        - 只显示当前用户SID信息"))
        print(_("    uac        - 只显示UAC设置"))
        print(_("  --lang, -l  - 设置显示语言（zh_CN 或 en_US）"))
        sys.exit(0)
    
    if len(sys.argv) < 2:
        print(_("Windows System Configuration (WSC) v") + __version__)
        print(_("使用方法: wsc <命令> [选项]"))
        print(_("可用命令:"))
        print(_("  system      - 获取系统基本信息"))
        print(_("  hardware    - 获取硬件信息"))
        print(_("  configuration - 获取系统配置信息"))
        print(_("  software    - 获取软件信息"))
        print(_("  network     - 获取网络配置信息"))
        print(_("  security    - 获取安全信息"))
        print(_("  all         - 获取所有系统信息"))
        print(_("  version     - 显示版本信息"))
        print(_("\n使用 wsc --help 查看详细帮助"))
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    # 处理带选项的命令
    subcommand = None
    if len(sys.argv) >= 3:
        subcommand = sys.argv[2].lower()
    
    if command == "version":
        print(_("Windows System Configuration (WSC) v") + __version__)
    elif command == "system":
        system_info = get_system_info()
        if subcommand == "basic":
            # 只显示基本系统信息
            basic_info = {
                "os_name": system_info.get("os_name", ""),
                "os_version": system_info.get("os_version", ""),
                "os_architecture": system_info.get("os_architecture", ""),
                "computer_name": system_info.get("computer_name", ""),
                "boot_time": system_info.get("boot_time", "")
            }
            print(json.dumps(basic_info, ensure_ascii=False, indent=2))
        elif subcommand == "os":
            # 只显示操作系统详细信息
            os_info = {
                "os_name": system_info.get("os_name", ""),
                "os_version": system_info.get("os_version", ""),
                "os_architecture": system_info.get("os_architecture", ""),
                "os_build": system_info.get("os_build", ""),
                "os_product_name": system_info.get("os_product_name", ""),
                "os_release_id": system_info.get("os_release_id", "")
            }
            print(json.dumps(os_info, ensure_ascii=False, indent=2))
        else:
            # 显示所有系统信息
            print(json.dumps(system_info, ensure_ascii=False, indent=2))
    elif command == "hardware":
        hardware_info = get_hardware_info()
        if subcommand == "cpu":
            # 只显示CPU信息
            print(json.dumps(hardware_info.get('cpu', {}), ensure_ascii=False, indent=2))
        elif subcommand == "memory":
            # 只显示内存信息
            print(json.dumps(hardware_info.get('memory', {}), ensure_ascii=False, indent=2))
        elif subcommand == "disks":
            # 只显示磁盘信息
            print(json.dumps(hardware_info.get('disks', []), ensure_ascii=False, indent=2))
        elif subcommand == "gpu":
            # 只显示GPU信息
            print(json.dumps(hardware_info.get('gpu', []), ensure_ascii=False, indent=2))
        elif subcommand == "motherboard":
            # 只显示主板信息
            print(json.dumps(hardware_info.get('motherboard', {}), ensure_ascii=False, indent=2))
        else:
            # 显示所有硬件信息
            print(json.dumps(hardware_info, ensure_ascii=False, indent=2))
    elif command == "configuration":
        print(json.dumps(get_configuration_info(), ensure_ascii=False, indent=2))
    elif command == "software":
        print(json.dumps(get_software_info(), ensure_ascii=False, indent=2))
    elif command == "network":
        network_info = get_network_info()
        if subcommand == "adapters":
            # 只显示传统适配器信息
            print(json.dumps(network_info['adapters'], ensure_ascii=False, indent=2))
        elif subcommand == "nic":
            # 只显示优化的网卡信息
            print(json.dumps(network_info['nic_info'], ensure_ascii=False, indent=2))
        elif subcommand == "ip":
            # 只显示IP地址信息
            print(json.dumps(network_info['ip_addresses'], ensure_ascii=False, indent=2))
        elif subcommand == "stats":
            # 只显示网络统计信息
            print(json.dumps(network_info['network_stats'], ensure_ascii=False, indent=2))
        elif subcommand == "connections":
            # 只显示网络连接信息
            print(json.dumps(network_info['network_connections'], ensure_ascii=False, indent=2))
        else:
            # 显示所有网络信息
            print(json.dumps(network_info, ensure_ascii=False, indent=2))
    elif command == "security":
        security_info = get_security_info()
        if subcommand == "users":
            # 只显示用户账户信息
            print(json.dumps(security_info.get('user_accounts', []), ensure_ascii=False, indent=2))
        elif subcommand == "groups":
            # 只显示用户组信息
            print(json.dumps(security_info.get('user_groups', []), ensure_ascii=False, indent=2))
        elif subcommand == "current":
            # 只显示当前用户信息
            print(json.dumps(security_info.get('current_user', {}), ensure_ascii=False, indent=2))
        elif subcommand == "sid":
            # 只显示当前用户SID信息
            from .security import SecurityInfo
            security = SecurityInfo()
            print(json.dumps(security.get_current_user_sid(), ensure_ascii=False, indent=2))
        elif subcommand == "uac":
            # 只显示UAC设置
            print(json.dumps(security_info.get('uac_settings', {}), ensure_ascii=False, indent=2))
        else:
            # 显示所有安全信息
            print(json.dumps(security_info, ensure_ascii=False, indent=2))
    elif command == "all":
        print(json.dumps(get_all_info(), ensure_ascii=False, indent=2))
    else:
        print(_("未知命令: %s") % command)
        print(_("使用 wsc --help 查看可用命令"))
        sys.exit(1)

# 添加简化的库名引用
class WSC:
    """Windows System Configuration (WSC) 简化访问类"""
    
    @staticmethod
    def get_all_info():
        """获取所有系统信息"""
        return get_all_info()
    
    @staticmethod
    def get_system_info():
        """获取系统基本信息"""
        return get_system_info()
    
    @staticmethod
    def get_hardware_info():
        """获取硬件信息"""
        return get_hardware_info()
    
    @staticmethod
    def get_configuration_info():
        """获取系统配置信息"""
        return get_configuration_info()
    
    @staticmethod
    def get_software_info():
        """获取软件信息"""
        return get_software_info()
    
    @staticmethod
    def get_network_info():
        """获取网络信息"""
        return get_network_info()
    
    @staticmethod
    def get_security_info():
        """获取安全信息"""
        return get_security_info()
    
    @staticmethod
    def get_current_user():
        """获取当前用户信息"""
        from .security import SecurityInfo
        security = SecurityInfo()
        return security.get_current_user()
    
    @staticmethod
    def get_current_user_sid():
        """使用wmic命令获取当前用户的用户名和SID"""
        from .security import SecurityInfo
        security = SecurityInfo()
        return security.get_current_user_sid()

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
    "WSC",
    
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
