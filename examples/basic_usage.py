"""Windows系统配置信息库基本使用示例"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wsc import (
    get_system_info,
    get_hardware_info,
    get_configuration_info,
    get_software_info,
    get_network_info,
    get_security_info,
    get_all_info,
    format_bytes,
    format_timestamp
)

def main():
    """主函数，演示库的基本使用"""
    # 获取系统基本信息
    print("=== 系统基本信息 ===")
    system_info = get_system_info()
    for key, value in system_info.items():
        if key == "boot_time":
            print(f"{key}: {format_timestamp(value)}")
        else:
            print(f"{key}: {value}")
    
    # 获取硬件信息
    print("\n=== 硬件信息 ===")
    hardware_info = get_hardware_info()
    
    # 显示CPU信息
    print("CPU信息:")
    cpu_info = hardware_info["cpu"]
    for key, value in cpu_info.items():
        print(f"  {key}: {value}")
    
    # 显示内存信息
    print("\n内存信息:")
    mem_info = hardware_info["memory"]
    for key, value in mem_info.items():
        if key in ["total", "available", "used"]:
            print(f"  {key}: {format_bytes(value)} ({value} bytes)")
        else:
            print(f"  {key}: {value}%")
    
    # 获取网络信息
    print("\n=== 网络信息 ===")
    network_info = get_network_info()
    print(f"主机名: {network_info['hostname']}")
    print(f"完全限定域名: {network_info['fqdn']}")
    
    print("\n网络适配器:")
    for adapter in network_info['adapters']:
        print(f"  描述: {adapter['description']}")
        print(f"  MAC地址: {adapter['mac_address']}")
        print(f"  IP地址: {', '.join(adapter['ip_addresses'])}")
        print(f"  默认网关: {adapter['default_gateway']}")
        print("  ---\n")
    
    # 获取所有信息（可选，会输出大量信息）
    # print("\n=== 所有系统信息 ===")
    # all_info = get_all_info()
    # print(all_info)

if __name__ == "__main__":
    main()
