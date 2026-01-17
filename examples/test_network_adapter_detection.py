#!/usr/bin/env python3
"""测试网卡识别功能"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wsc import NetworkInfo

def main():
    """主测试函数"""
    print("=== 网卡识别功能测试 ===")
    
    network = NetworkInfo()
    
    # 获取优化的网卡信息
    enhanced_adapters = network.get_nic_info()
    
    print(f"发现 {len(enhanced_adapters)} 个网络适配器\n")
    
    for i, adapter in enumerate(enhanced_adapters, 1):
        print(f"--- 网卡 {i}: {adapter.get('guid', 'N/A')} ---")
        print(f"  MAC地址: {adapter['mac_address']}")
        print(f"  物理地址: {adapter['physical_address']}")
        print(f"  索引: {adapter['index']}")
        print(f"  适配器类型: {adapter['adapter_type']}")
        print(f"  连接类型: {adapter['connection_type']}")
        print(f"  已启用: {'是' if adapter['net_enabled'] else '否'}")
        print(f"  物理适配器: {'是' if adapter['physical_adapter'] else '否'}")
        print(f"  IP地址: {', '.join(adapter['ip_addresses'])}")
        print(f"  子网掩码: {', '.join(adapter['subnet_masks'])}")
        print(f"  默认网关: {adapter['default_gateway']}")
        print(f"  DNS服务器: {', '.join(adapter['dns_servers'])}")
        print()
    
    # 统计不同类型的网卡
    type_counts = {}
    for adapter in enhanced_adapters:
        adapter_type = adapter['adapter_type']
        type_counts[adapter_type] = type_counts.get(adapter_type, 0) + 1
    
    print("=== 网卡类型统计 ===")
    for adapter_type, count in type_counts.items():
        print(f"  {adapter_type}: {count} 个")
    
    # 统计不同连接类型的网卡
    connection_type_counts = {}
    for adapter in enhanced_adapters:
        connection_type = adapter['connection_type']
        connection_type_counts[connection_type] = connection_type_counts.get(connection_type, 0) + 1
    
    print("\n=== 连接类型统计 ===")
    for connection_type, count in connection_type_counts.items():
        print(f"  {connection_type}: {count} 个")
    
    print("\n=== 启用状态统计 ===")
    status_counts = {}
    for adapter in enhanced_adapters:
        status = "已启用" if adapter['net_enabled'] else "已禁用"
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"  {status}: {count} 个")
    
    print("\n网卡识别功能测试完成！")

if __name__ == "__main__":
    main()
