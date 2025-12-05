"""Windows系统配置信息库测试脚本"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wsc import (
    SystemInfo,
    HardwareInfo,
    ConfigurationInfo,
    SoftwareInfo,
    NetworkInfo,
    SecurityInfo,
    format_bytes,
    format_timestamp
)

def test_system_info():
    """测试系统基本信息模块"""
    print("=== 测试系统基本信息模块 ===")
    system = SystemInfo()
    print(f"系统名称: {system.get_os_name()}")
    print(f"系统版本: {system.get_os_version()}")
    print(f"系统构建号: {system.get_os_build()}")
    print(f"系统架构: {system.get_system_architecture()}")
    print(f"系统启动时间: {format_timestamp(system.get_boot_time())}")
    print(f"计算机名称: {system.get_computer_name()}")
    print(f"域名: {system.get_domain_name()}")
    print(f"系统目录: {system.get_system_directory()}")
    print(f"临时目录: {system.get_temp_directory()}")
    print()

def test_hardware_info():
    """测试硬件信息模块"""
    print("=== 测试硬件信息模块 ===")
    hardware = HardwareInfo()
    cpu_info = hardware.get_cpu_info()
    print(f"CPU型号: {cpu_info['model']}")
    print(f"CPU核心数: {cpu_info['cores']}")
    
    mem_info = hardware.get_memory_info()
    print(f"内存总量: {format_bytes(mem_info['total'])}")
    print(f"可用内存: {format_bytes(mem_info['available'])}")
    
    disks = hardware.get_disk_info()
    print(f"硬盘数量: {len(disks)}")
    if disks:
        print(f"第一块硬盘: {disks[0]['model']}")
    
    adapters = hardware.get_network_adapters()
    print(f"网络适配器数量: {len(adapters)}")
    print()

def test_configuration_info():
    """测试系统配置模块"""
    print("=== 测试系统配置模块 ===")
    config = ConfigurationInfo()
    print(f"环境变量数量: {len(config.get_environment_variables())}")
    
    # 只获取前5个启动项
    startup_items = config.get_startup_items()
    print(f"启动项数量: {len(startup_items)}")
    print(f"前5个启动项: {[item['name'] for item in startup_items[:5]]}")
    
    power_plans = config.get_power_plans()
    print(f"电源计划数量: {len(power_plans)}")
    print()

def test_software_info():
    """测试软件信息模块"""
    print("=== 测试软件信息模块 ===")
    software = SoftwareInfo()
    
    # 只获取前5个正在运行的进程
    processes = software.get_running_processes()
    print(f"正在运行的进程数量: {len(processes)}")
    print(f"前5个进程: {[p['name'] for p in processes[:5]]}")
    
    startup_programs = software.get_startup_programs()
    print(f"启动程序数量: {len(startup_programs)}")
    print()

def test_network_info():
    """测试网络配置模块"""
    print("=== 测试网络配置模块 ===")
    network = NetworkInfo()
    print(f"主机名: {network.get_hostname()}")
    print(f"完全限定域名: {network.get_fqdn()}")
    
    adapters = network.get_network_adapters()
    print(f"网络适配器数量: {len(adapters)}")
    
    dns_servers = network.get_dns_servers()
    print(f"DNS服务器数量: {len(dns_servers)}")
    if dns_servers:
        print(f"DNS服务器: {dns_servers}")
    
    gateway = network.get_default_gateway()
    print(f"默认网关: {gateway}")
    print()

def test_security_info():
    """测试安全信息模块"""
    print("=== 测试安全信息模块 ===")
    security = SecurityInfo()
    print(f"当前用户: {security.get_current_user()['username']}")
    
    groups = security.get_user_groups()
    print(f"用户组数量: {len(groups)}")
    
    # 只获取管理员组的前5个成员
    admin_members = security.get_group_members("Administrators")
    print(f"管理员组成员数量: {len(admin_members)}")
    print(f"前5个管理员组成员: {[m['name'] for m in admin_members[:5]]}")
    print()

def main():
    """主测试函数"""
    print("开始测试Windows系统配置信息库...\n")
    
    test_system_info()
    test_hardware_info()
    test_configuration_info()
    test_software_info()
    test_network_info()
    test_security_info()
    
    print("所有模块测试完成！")

if __name__ == "__main__":
    main()
