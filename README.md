# Windows-System-Configuration (WSC) 库使用手册

## 1. 库介绍

Windows System Configuration (WSC) 是一个纯Python编写的Windows系统配置信息获取库，**无需任何第三方依赖**，完全使用Windows内置命令行工具和Python标准库实现。

### 主要功能

- **系统基本信息**：操作系统版本、构建号、架构、启动时间等
- **硬件信息**：CPU、内存、硬盘、USB设备、分区、GPU、主板、BIOS等
- **系统配置**：环境变量、服务、启动项、电源计划、Windows更新设置、UAC设置等
- **软件信息**：已安装程序、运行进程、驱动程序、启动程序、Windows功能等
- **网络配置**：网络适配器、IP地址、网络统计、连接、DNS服务器、默认网关等
- **安全信息**：用户账户、用户组、组成员、当前用户、Windows Defender状态、防火墙规则等

## 2. 安装方法

### 2.1 使用pip安装

```bash
# 从本地wheel文件安装
pip install Windows-System-Configuration-0.1.1-py3-none-any.whl

# 或从远程仓库安装（如果已发布到PyPI）
pip install Windows-System-Configuration
```

### 2.2 从源码安装

```bash
git clone https://github.com/508364/Windows-System-Configuration_WSC.git
cd Windows-System-Configuration_WSC
pip install -e .
```

## 3. 快速开始

### 3.1 基本使用

```python
from wsc import get_all_info

# 获取所有系统信息
all_info = get_all_info()
print("系统名称:", all_info["system"]["os_name"])
print("CPU型号:", all_info["hardware"]["cpu"]["model"])
print("内存总量:", all_info["hardware"]["memory"]["total"])
print("硬盘数量:", len(all_info["hardware"]["disks"]))
print("当前用户:", all_info["security"]["current_user"]["username"])
```

### 3.2 按模块获取信息

```python
from wsc import (
    get_system_info,
    get_hardware_info,
    get_configuration_info,
    get_software_info,
    get_network_info,
    get_security_info
)

# 获取系统基本信息
system_info = get_system_info()
print("操作系统版本:", system_info["os_version"])
print("系统启动时间:", system_info["boot_time"])

# 获取硬件信息
hardware_info = get_hardware_info()
print("CPU核心数:", hardware_info["cpu"]["cores"])
print("可用内存:", hardware_info["memory"]["available"])

# 获取网络信息
network_info = get_network_info()
print("主机名:", network_info["hostname"])
print("默认网关:", network_info["default_gateway"])
```

### 3.3 使用类实例

```python
from wsc import (
    SystemInfo,
    HardwareInfo,
    NetworkInfo
)

# 创建硬件信息对象
hardware = HardwareInfo()

# 获取CPU信息
cpu = hardware.get_cpu_info()
print("CPU型号:", cpu["model"])
print("CPU核心数:", cpu["cores"])

# 获取内存信息
memory = hardware.get_memory_info()
print("内存总量:", memory["total"])
print("可用内存:", memory["available"])
print("内存使用率:", memory["percent"])

# 获取硬盘信息
disks = hardware.get_disk_info()
print(f"找到 {len(disks)} 块硬盘")
for disk in disks:
    print(f"  - {disk['model']} ({disk['size']} 字节)")

# 获取USB存储设备
usb_devices = hardware.get_usb_storage_info()
print(f"找到 {len(usb_devices)} 个USB存储设备")
for usb in usb_devices:
    print(f"  - {usb['model']} ({usb['size']} 字节)")

# 获取网络适配器
network = NetworkInfo()
adapters = network.get_network_adapters()
print(f"找到 {len(adapters)} 个网络适配器")
```

### 3.4 使用简化的WSC类（推荐）

```python
from wsc import WSC

# 获取所有系统信息
all_info = WSC.get_all_info()
print("系统名称:", all_info["system"]["os_name"])
print("CPU型号:", all_info["hardware"]["cpu"]["model"])

# 获取当前用户的SID
current_user_sid = WSC.get_current_user_sid()
print(f"当前用户名: {current_user_sid['username']}")
print(f"SID: {current_user_sid['sid']}")
print(f"域名: {current_user_sid['domain']}")

# 获取网卡信息
nic_info = WSC.get_network_info()['nic_info']
for adapter in nic_info:
    print(f"\n网卡MAC: {adapter['mac_address']}")
    print(f"类型: {adapter['adapter_type']}")
    print(f"连接类型: {adapter['connection_type']}")
    print(f"已启用: {'是' if adapter['net_enabled'] else '否'}")
```

## 4. 命令行工具

WSC库提供了便捷的命令行工具 `wsc`，可以直接从命令行获取系统信息。

### 4.1 命令列表

```
Windows-System-Configuration (WSC) v0.1.1
使用方法: wsc <命令> [选项]
可用命令:
  system      - 获取系统基本信息
  hardware    - 获取硬件信息
  configuration - 获取系统配置信息
  software    - 获取软件信息
  network     - 获取网络配置信息
  security    - 获取安全信息
  all         - 获取所有系统信息
  version     - 显示版本信息

可用选项:
  system <选项>:
    basic      - 只显示基本系统信息
    os         - 只显示操作系统详细信息
  hardware <选项>:
    cpu        - 只显示CPU信息
    memory     - 只显示内存信息
    disks      - 只显示磁盘信息
    gpu        - 只显示GPU信息
    motherboard - 只显示主板信息
  network <选项>:
    adapters   - 只显示传统网络适配器信息
    nic        - 只显示优化的网卡信息（推荐）
    ip         - 只显示IP地址信息
    stats      - 只显示网络统计信息
    connections - 只显示网络连接信息
  security <选项>:
    users      - 只显示用户账户信息
    groups     - 只显示用户组信息
    current    - 只显示当前用户信息
    sid        - 只显示当前用户SID信息
    uac        - 只显示UAC设置
  --help, -h  - 显示帮助信息
  --lang, -l  - 设置显示语言（zh_CN 或 en_US）
```

### 4.2 使用示例

```bash
# 显示库版本
wsc version

# 获取系统基本信息
wsc system

# 只获取基本系统信息
wsc system basic

# 只获取操作系统详细信息
wsc system os

# 获取完整硬件信息
wsc hardware

# 只获取CPU信息
wsc hardware cpu

# 只获取内存信息
wsc hardware memory

# 只获取磁盘信息
wsc hardware disks

# 获取完整网络信息
wsc network

# 只获取优化的网卡信息（推荐）
wsc network nic

# 只获取IP地址信息
wsc network ip

# 只获取网络连接信息
wsc network connections

# 获取完整安全信息
wsc security

# 只获取用户账户信息
wsc security users

# 只获取当前用户SID信息
wsc security sid

# 获取所有系统信息（JSON格式）
wsc all > system_info.json

# 显示帮助信息
wsc --help

# 使用英文显示帮助信息
wsc --lang en_US --help

# 使用英文获取系统基本信息
wsc --lang en_US system

# 使用中文显示版本信息
wsc --lang zh_CN version
```

### 4.3 多语言支持

WSC库支持中文和英文两种语言，会根据系统主语言自动切换显示语言，默认使用中文。可以通过`--lang`或`-l`选项手动切换语言。

**支持的语言：**
- `zh_CN` - 中文
- `en_US` - English

**自动检测：**
WSC库会自动检测系统主语言，并使用对应的语言显示帮助信息和提示。例如：
- 如果系统语言是中文，会默认显示中文
- 如果系统语言是英文，会默认显示英文
- 如果系统语言是其他语言，会默认显示中文

**手动切换：**
可以使用`--lang`或`-l`选项手动指定语言，覆盖系统自动检测的结果。

**使用示例：**

```bash
# 自动根据系统语言显示帮助信息
wsc --help

# 手动指定使用英文显示帮助信息
wsc -l en_US --help

# 手动指定使用中文获取硬件信息
wsc -l zh_CN hardware
```

## 5. 核心模块详细说明

### 5.1 系统信息模块 (SystemInfo)

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `get_os_version()` | 获取操作系统版本 | 字符串 |
| `get_os_name()` | 获取操作系统名称 | 字符串 |
| `get_os_build()` | 获取操作系统构建号 | 字符串 |
| `get_boot_time()` | 获取系统启动时间 | 时间戳 |
| `get_computer_name()` | 获取计算机名称 | 字符串 |
| `get_domain_name()` | 获取域名 | 字符串 |
| `get_all_info()` | 获取所有系统信息 | 字典 |

### 5.2 硬件信息模块 (HardwareInfo)

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `get_cpu_info()` | 获取CPU信息 | 字典 |
| `get_memory_info()` | 获取内存信息 | 字典 |
| `get_disk_info()` | 获取硬盘信息（排除USB） | 列表 |
| `get_usb_storage_info()` | 获取USB存储设备信息 | 列表 |
| `get_partition_info()` | 获取分区信息 | 列表 |
| `get_gpu_info()` | 获取GPU信息 | 列表 |
| `get_motherboard_info()` | 获取主板信息 | 字典 |
| `get_network_adapters()` | 获取网络适配器信息 | 列表 |
| `get_bios_info()` | 获取BIOS信息 | 字典 |
| `get_all_hardware_info()` | 获取所有硬件信息 | 字典 |

### 5.3 网络配置模块 (NetworkInfo)

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `get_network_adapters()` | 获取网络适配器列表 | 列表 |
| `get_nic_info()` | 获取优化的网卡信息（推荐） | 列表 |
| `get_ip_addresses()` | 获取所有IP地址 | 列表 |
| `get_network_stats()` | 获取网络统计信息 | 字典 |
| `get_network_connections()` | 获取网络连接列表 | 列表 |
| `get_dns_servers()` | 获取DNS服务器列表 | 列表 |
| `get_default_gateway()` | 获取默认网关 | 字符串 |
| `get_hostname()` | 获取主机名 | 字符串 |
| `get_all_network_info()` | 获取所有网络信息 | 字典 |

### 5.4 安全模块 (SecurityInfo)

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `get_user_accounts()` | 获取用户账户列表 | 列表 |
| `get_user_groups()` | 获取用户组列表 | 列表 |
| `get_group_members(group_name)` | 获取特定组的成员列表 | 列表 |
| `get_current_user()` | 获取当前登录用户 | 字典 |
| `get_current_user_sid()` | 获取当前用户的SID | 字典 |
| `get_uac_settings()` | 获取UAC设置 | 字典 |
| `get_windows_defender_status()` | 获取Windows Defender状态 | 字典 |
| `get_firewall_rules()` | 获取防火墙规则列表 | 列表 |

### 5.5 其他模块

- **ConfigurationInfo**：系统配置信息
- **SoftwareInfo**：软件信息

## 6. 工具函数

WSC库提供了一些实用的工具函数：

| 函数 | 说明 |
|------|------|
| `format_bytes(size_bytes)` | 将字节大小格式化为可读单位 |
| `format_timestamp(timestamp)` | 将时间戳转换为可读日期时间 |
| `read_registry_value(key_path, value_name)` | 安全读取注册表值 |
| `get_registry_subkeys(key_path)` | 获取注册表子键列表 |
| `get_registry_values(key_path)` | 获取注册表键下所有值 |
| `safe_int(value, default=0)` | 安全转换为整数 |
| `safe_float(value, default=0.0)` | 安全转换为浮点数 |

## 7. 示例应用

### 7.1 监控系统状态

```python
from wsc import get_hardware_info, get_network_info
from wsc.utils import format_bytes

# 获取系统资源使用情况
hardware = get_hardware_info()

print("=== 系统资源监控 ===")
print(f"CPU: {hardware['cpu']['model']}")
print(f"内存总量: {format_bytes(hardware['memory']['total'])}")
print(f"可用内存: {format_bytes(hardware['memory']['available'])}")
print(f"内存使用率: {hardware['memory']['percent']}%")

# 获取网络连接情况
network = get_network_info()
print(f"\n=== 网络监控 ===")
print(f"主机名: {network['hostname']}")
print(f"默认网关: {network['default_gateway']}")
print(f"活跃连接数: {len(network['network_connections'])}")
```

### 7.2 生成系统报告

```python
from wsc import get_all_info
import json

# 获取所有系统信息
all_info = get_all_info()

# 保存为JSON文件
with open("system_report.json", "w", encoding="utf-8") as f:
    json.dump(all_info, f, ensure_ascii=False, indent=2)

print("系统报告已保存到 system_report.json")
```

## 8. 注意事项

1. **兼容性**：支持Windows 7及以上版本，Python 3.6及以上版本
2. **权限要求**：部分操作需要管理员权限，如获取完整的系统服务信息
3. **性能**：某些命令可能需要较长时间执行，建议异步使用
4. **命令行依赖**：依赖以下Windows内置命令：
   - `wmic`：获取硬件、系统、软件等信息
   - `ipconfig`：获取网络配置
   - `route`：获取路由表
   - `netstat`：获取网络连接
   - `netsh`：获取网络配置和防火墙规则
   - `sc`：获取系统服务
   - `powercfg`：获取电源计划
   - `tasklist`：获取运行进程
   - `whoami`：获取当前用户
   - `net`：获取用户和组信息
   - `dism`：获取Windows功能

## 9. 常见问题

### Q: 为什么获取不到某些信息？
A: 可能的原因：
- 权限不足，尝试以管理员身份运行
- 相关Windows命令在当前系统版本不可用
- 硬件设备可能未正确识别

### Q: 为什么获取的信息不准确？
A: WSC库依赖Windows命令行工具的输出，某些命令的输出格式可能因Windows版本而异。

### Q: 可以在非Windows系统上使用吗？
A: 不可以，WSC库专门为Windows系统设计，依赖Windows内置命令。

## 10. 版本历史

- **v0.1.1**：优化版本
  - 新增优化的网卡识别功能（`get_nic_info()`）
  - 新增简化的WSC类访问方式
  - 新增获取当前用户SID的功能
  - 增强命令行工具，支持只显示网卡信息（`wsc network nic`）
  - 优化文档，添加更多使用示例
  - 修复命令行工具的--help参数问题

- **v0.1.0**：初始版本
  - 实现所有核心功能模块
  - 支持命令行工具
  - 无第三方依赖

## 11. 贡献

欢迎提交Issue和Pull Request来改进WSC库！

## 12. 许可证

MIT License

## 13. 联系方式

- 作者：508364
- 邮箱：github508364@qq.com
- 项目地址：https://github.com/508364/Windows-System-Configuration_WSC

---

Windows-System-Configuration (WSC) © 2025
