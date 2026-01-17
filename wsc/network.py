import subprocess
import re
import socket

class NetworkInfo:
    """Windows网络配置信息获取类，使用命令行工具获取信息"""
    
    def __init__(self):
        """初始化"""
        pass
    
    def _run_cmd(self, cmd):
        """执行命令行命令并返回输出"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='gbk')
            return result.stdout
        except Exception:
            # 尝试使用utf-8编码
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
            return result.stdout
    
    def get_network_adapters(self):
        """使用ipconfig /all获取网络适配器列表"""
        adapters = []
        output = self._run_cmd('ipconfig /all')
        
        # 分割输出为适配器块
        adapter_blocks = output.split('\n\n')
        
        for block in adapter_blocks:
            if '适配器' not in block and 'Adapter' not in block:
                continue
            
            adapter_info = {
                "description": "",
                "adapter_name": "",
                "mac_address": "",
                "ip_addresses": [],
                "subnet_masks": [],
                "default_gateway": None,
                "dns_servers": [],
                "dhcp_enabled": False,
                "dhcp_server": "",
                "dns_domain": ""
            }
            
            # 解析适配器名称
            name_match = re.search(r'(?:适配器|Adapter) (.+?):', block)
            if name_match:
                adapter_info['adapter_name'] = name_match.group(1)
            
            # 解析描述
            desc_match = re.search(r'描述[.:\s]+(.+)', block)
            if desc_match:
                adapter_info['description'] = desc_match.group(1)
            
            # 解析物理地址（MAC）
            mac_match = re.search(r'物理地址[.:\s]+([0-9A-Fa-f:-]+)', block)
            if mac_match:
                adapter_info['mac_address'] = mac_match.group(1)
            
            # 解析IPv4地址
            ipv4_match = re.search(r'IPv4 地址[.:\s]+([0-9.]+)', block)
            if ipv4_match:
                adapter_info['ip_addresses'].append(ipv4_match.group(1))
            
            # 解析子网掩码
            subnet_match = re.search(r'子网掩码[.:\s]+([0-9.]+)', block)
            if subnet_match:
                adapter_info['subnet_masks'].append(subnet_match.group(1))
            
            # 解析默认网关
            gateway_match = re.search(r'默认网关[.:\s]+([0-9.]+)', block)
            if gateway_match:
                adapter_info['default_gateway'] = gateway_match.group(1)
            
            # 解析DNS服务器
            dns_matches = re.findall(r'DNS 服务器[.:\s]+([0-9.]+)', block)
            adapter_info['dns_servers'].extend(dns_matches)
            
            # 解析DHCP启用状态
            dhcp_match = re.search(r'DHCP 已启用[.:\s]+(是|否|Yes|No)', block)
            if dhcp_match:
                dhcp_val = dhcp_match.group(1)
                adapter_info['dhcp_enabled'] = dhcp_val in ['是', 'Yes']
            
            # 解析DHCP服务器
            dhcp_server_match = re.search(r'DHCP 服务器[.:\s]+([0-9.]+)', block)
            if dhcp_server_match:
                adapter_info['dhcp_server'] = dhcp_server_match.group(1)
            
            # 解析DNS域
            dns_domain_match = re.search(r'DNS 后缀搜索列表[.:\s]+(.+)', block)
            if dns_domain_match:
                adapter_info['dns_domain'] = dns_domain_match.group(1)
            
            adapters.append(adapter_info)
        
        return adapters
    
    def get_ip_addresses(self):
        """使用ipconfig获取所有IP地址"""
        ip_addresses = []
        output = self._run_cmd('ipconfig')
        
        # 解析IPv4地址
        ipv4_matches = re.findall(r'IPv4 地址[.:\s]+([0-9.]+)', output)
        for ip in ipv4_matches:
            ip_addresses.append({"ip": ip})
        
        return ip_addresses
    
    def get_network_stats(self):
        """使用netstat -e获取网络统计信息"""
        stats = {}
        output = self._run_cmd('netstat -e')
        
        # 解析统计信息
        bytes_recv_match = re.search(r'接收的字节数[\s]+([0-9,]+)', output)
        bytes_sent_match = re.search(r'发送的字节数[\s]+([0-9,]+)', output)
        packets_recv_match = re.search(r'接收的数据包[\s]+([0-9,]+)', output)
        packets_sent_match = re.search(r'发送的数据包[\s]+([0-9,]+)', output)
        
        if bytes_recv_match and bytes_sent_match:
            stats['total'] = {
                "bytes_sent": int(bytes_sent_match.group(1).replace(',', '')),
                "bytes_recv": int(bytes_recv_match.group(1).replace(',', '')),
                "packets_sent": int(packets_sent_match.group(1).replace(',', '')) if packets_sent_match else 0,
                "packets_recv": int(packets_recv_match.group(1).replace(',', '')) if packets_recv_match else 0
            }
        
        return stats
    
    def get_network_connections(self):
        """使用netstat -ano获取网络连接列表"""
        connections = []
        output = self._run_cmd('netstat -ano')
        
        lines = output.strip().split('\n')
        # 跳过标题行
        if len(lines) >= 3:
            lines = lines[3:]
        
        for line in lines:
            if not line.strip():
                continue
            
            # 解析netstat输出
            parts = re.split(r'\s+', line.strip())
            if len(parts) >= 5:
                proto = parts[0]
                local_addr = parts[1]
                foreign_addr = parts[2]
                state = parts[3] if len(parts) > 4 else ''
                pid = parts[-1]
                
                connections.append({
                    "proto": proto,
                    "local_addr": local_addr,
                    "foreign_addr": foreign_addr,
                    "state": state,
                    "pid": int(pid) if pid.isdigit() else None
                })
        
        return connections
    
    def get_dns_servers(self):
        """使用ipconfig /all获取DNS服务器列表"""
        dns_servers = []
        output = self._run_cmd('ipconfig /all')
        
        # 解析DNS服务器
        dns_matches = re.findall(r'DNS 服务器[.:\s]+([0-9.]+)', output)
        # 去重
        dns_servers = list(set(dns_matches))
        
        return dns_servers
    
    def get_default_gateway(self):
        """使用ipconfig /all获取默认网关，优先返回物理网络适配器的网关"""
        output = self._run_cmd('ipconfig /all')
        
        # 虚拟适配器名称列表，我们应该优先选择物理适配器
        virtual_adapters = ['VPN', 'VirtualBox', 'Teredo', 'VMware', 'Hyper-V', 'Docker']
        
        # 按适配器分割输出
        adapter_blocks = output.split('\n\n')
        
        # 优先查找物理适配器的默认网关
        for block in adapter_blocks:
            # 跳过虚拟适配器
            if any(virtual in block for virtual in virtual_adapters):
                continue
            
            # 查找默认网关
            gateway_match = re.search(r'默认网关[.:\s]+([0-9.]+)', block)
            if gateway_match:
                return gateway_match.group(1)
        
        # 如果没有找到物理适配器的网关，尝试查找所有适配器
        for block in adapter_blocks:
            gateway_match = re.search(r'默认网关[.:\s]+([0-9.]+)', block)
            if gateway_match:
                return gateway_match.group(1)
        
        # 尝试英文格式
        for block in adapter_blocks:
            gateway_match = re.search(r'Default Gateway[.:\s]+([0-9.]+)', block)
            if gateway_match:
                return gateway_match.group(1)
                
        return None
    
    def get_hostname(self):
        """获取主机名"""
        return socket.gethostname()
    
    def get_fqdn(self):
        """获取完全限定域名"""
        return socket.getfqdn()
    
    def get_network_profiles(self):
        """使用netsh获取网络配置文件"""
        profiles = []
        output = self._run_cmd('netsh wlan show profiles')
        
        # 解析网络配置文件名称
        profile_names = re.findall(r'所有用户配置文件 : (.+)', output)
        
        for profile_name in profile_names:
            # 获取每个配置文件的详细信息
            profile_output = self._run_cmd(f'netsh wlan show profile name="{profile_name}"')
            
            profile_info = {
                "name": profile_name,
                "ssid": "",
                "authentication": "",
                "encryption": ""
            }
            
            # 解析SSID
            ssid_match = re.search(r'SSID 名称[.:\s]+(.+)', profile_output)
            if ssid_match:
                profile_info['ssid'] = ssid_match.group(1)
            
            # 解析身份验证
            auth_match = re.search(r'身份验证[.:\s]+(.+)', profile_output)
            if auth_match:
                profile_info['authentication'] = auth_match.group(1)
            
            # 解析加密
            encrypt_match = re.search(r'加密[.:\s]+(.+)', profile_output)
            if encrypt_match:
                profile_info['encryption'] = encrypt_match.group(1)
            
            profiles.append(profile_info)
        
        return profiles
    
    def get_firewall_status(self):
        """使用netsh advfirewall show allprofiles获取防火墙状态"""
        output = self._run_cmd('netsh advfirewall show allprofiles')
        
        firewall_status = {
            "domain_profile": "",
            "private_profile": "",
            "public_profile": ""
        }
        
        # 解析域名配置文件状态
        domain_match = re.search(r'域名配置文件状态[.:\s]+(.+)', output)
        if domain_match:
            firewall_status['domain_profile'] = domain_match.group(1)
        
        # 解析专用配置文件状态
        private_match = re.search(r'专用配置文件状态[.:\s]+(.+)', output)
        if private_match:
            firewall_status['private_profile'] = private_match.group(1)
        
        # 解析公用配置文件状态
        public_match = re.search(r'公用配置文件状态[.:\s]+(.+)', output)
        if public_match:
            firewall_status['public_profile'] = public_match.group(1)
        
        return firewall_status
    
    def get_nic_info(self):
        """获取优化的网卡信息，按照用户要求的逻辑实现"""
        import re
        from .utils import safe_int
        
        # 定义网卡信息列表
        nic_list = []
        
        # 1. 获取Win32_NetworkAdapter信息
        # 使用普通格式而不是list格式，更易于解析
        win32_nic_cmd = 'wmic Path Win32_NetworkAdapter get GUID,MACAddress,NetEnabled,PhysicalAdapter,Index'
        win32_nic_output = self._run_cmd(win32_nic_cmd)
        
        # 解析Win32_NetworkAdapter输出
        win32_nic_info = []
        lines = win32_nic_output.strip().split('\n')
        if len(lines) < 2:
            # 没有网卡数据
            pass
        else:
            # 跳过标题行，处理数据行
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                
                # 解析数据行，注意字段顺序：GUID, MACAddress, NetEnabled, PhysicalAdapter, Index
                # 使用正则表达式提取字段值
                # 查找MAC地址（格式：XX:XX:XX:XX:XX:XX）
                mac_pattern = r'([0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5})'
                mac_match = re.search(mac_pattern, line)
                if not mac_match:
                    continue
                
                mac_address = mac_match.group(1)
                
                # 提取GUID（格式：{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}）
                guid_pattern = r'({[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}})'
                guid_match = re.search(guid_pattern, line)
                guid = guid_match.group(1) if guid_match else ''
                
                # 提取Index（数字）
                index_pattern = r'\b(\d+)\b'
                index_matches = re.findall(index_pattern, line)
                index = index_matches[-1] if index_matches else ''
                
                # 提取NetEnabled（TRUE/FALSE）
                net_enabled = 'TRUE' in line.upper()
                
                # 提取PhysicalAdapter（TRUE/FALSE）
                physical_adapter = 'TRUE' in line.upper() and ('PHYSICAL' in line.upper() or 'TRUE' in line.upper().split())
                
                # 创建网卡信息
                nic_info = {
                    'GUID': guid,
                    'MACAddress': mac_address,
                    'NetEnabled': 'TRUE' if net_enabled else 'FALSE',
                    'PhysicalAdapter': 'TRUE' if physical_adapter else 'FALSE',
                    'Index': index
                }
                
                win32_nic_info.append(nic_info)
        
        # 2. 获取Win32_NetworkAdapterConfiguration信息
        # 使用普通格式而不是list格式，更易于解析
        win32_nic_config_cmd = 'wmic Path Win32_NetworkAdapterConfiguration get IPEnabled,MACAddress,SettingID,IPAddress,IPSubnet,Index'
        win32_nic_config_output = self._run_cmd(win32_nic_config_cmd)
        
        # 解析Win32_NetworkAdapterConfiguration输出
        win32_nic_config_info = []
        lines = win32_nic_config_output.strip().split('\n')
        if len(lines) >= 2:
            # 跳过标题行，处理数据行
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                
                # 查找MAC地址（格式：XX:XX:XX:XX:XX:XX）
                mac_pattern = r'([0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5})'
                mac_match = re.search(mac_pattern, line)
                if not mac_match:
                    continue
                
                mac_address = mac_match.group(1)
                
                # 提取SettingID（格式：{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}）
                setting_id_pattern = r'({[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}})'
                setting_id_match = re.search(setting_id_pattern, line)
                setting_id = setting_id_match.group(1) if setting_id_match else ''
                
                # 提取Index（数字）
                index_pattern = r'\b(\d+)\b'
                index_matches = re.findall(index_pattern, line)
                index = index_matches[-1] if index_matches else ''
                
                # 提取IPEnabled（TRUE/FALSE）
                ip_enabled = 'TRUE' in line.upper()
                
                # 创建配置信息
                config_info = {
                    'IPEnabled': 'TRUE' if ip_enabled else 'FALSE',
                    'MACAddress': mac_address,
                    'SettingID': setting_id,
                    'IPAddress': '',
                    'IPSubnet': '',
                    'Index': index
                }
                
                win32_nic_config_info.append(config_info)
        
        # 3. 解析注册表获取Characteristics值（用于区分物理/虚拟网卡）
        def get_registry_characteristics(index):
            """从注册表获取Characteristics值"""
            import winreg
            try:
                # 尝试不同的索引格式
                for index_format in ['{:04d}', '{}']:
                    try:
                        reg_path = r'SYSTEM\ControlSet001\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\{}'.format(index_format.format(int(index)))
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
                        characteristics, _ = winreg.QueryValueEx(key, 'Characteristics')
                        winreg.CloseKey(key)
                        return characteristics
                    except Exception:
                        continue
                return 0
            except Exception:
                return 0
        
        # 4. 解析注册表判断是否为无线网卡
        def is_wireless_nic(index):
            """判断是否为无线网卡"""
            import winreg
            try:
                # 方法1：检查MediaSubType
                for index_format in ['{:04d}', '{}']:
                    try:
                        reg_path = r'SYSTEM\CurrentControlSet\Control\Network\{4D36E972-E325-11CE-BFC1-08002BE10318}\{}'.format(index_format.format(int(index)))
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
                        media_subtype, _ = winreg.QueryValueEx(key, 'MediaSubType')
                        winreg.CloseKey(key)
                        if media_subtype == 2:
                            return True
                        break
                    except Exception:
                        continue
            except Exception:
                pass
            
            try:
                # 方法2：检查LowerRange
                for index_format in ['{:04d}', '{}']:
                    try:
                        reg_path = r'SYSTEM\ControlSet001\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\{}'.format(index_format.format(int(index)))
                        reg_path += r'\Ndi\Interfaces'
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
                        lower_range, _ = winreg.QueryValueEx(key, 'LowerRange')
                        winreg.CloseKey(key)
                        if any(keyword in lower_range.lower() for keyword in ['wifi', 'wlan']):
                            return True
                        break
                    except Exception:
                        continue
            except Exception:
                pass
            
            return False
        
        # 创建MAC地址到配置信息的映射
        mac_to_config = {}
        for config in win32_nic_config_info:
            mac = config.get('MACAddress', '').upper()
            if mac:
                mac_to_config[mac] = config
        
        # 5. 处理Win32_NetworkAdapter信息（适用于Win7+）
        for nic in win32_nic_info:
            # 跳过无效数据
            mac_address = nic.get('MACAddress', '').strip()
            if not mac_address:
                continue
            
            # 获取基本字段值
            guid = nic.get('GUID', '').strip()
            index = nic.get('Index', '').strip()
            net_enabled = nic.get('NetEnabled', '').strip().upper() == 'TRUE'
            physical_adapter = nic.get('PhysicalAdapter', '').strip().upper() == 'TRUE'
            
            # 获取网卡基本信息
            nic_info = {
                'guid': guid,
                'mac_address': mac_address,
                'physical_address': mac_address,
                'index': index,
                'net_enabled': net_enabled,
                'physical_adapter': physical_adapter,
                'adapter_type': 'Physical' if physical_adapter else 'Virtual',
                'connection_type': 'Unknown',
                'ip_addresses': [],
                'subnet_masks': [],
                'default_gateway': None,
                'dns_servers': []
            }
            
            # 6. 关联Win32_NetworkAdapterConfiguration信息
            mac_upper = mac_address.upper()
            if mac_upper in mac_to_config:
                config = mac_to_config[mac_upper]
                # 解析IP地址
                if config.get('IPAddress'):
                    ip_addresses = re.findall(r'"([^"]+)"', config['IPAddress'])
                    nic_info['ip_addresses'] = ip_addresses
                # 解析子网掩码
                if config.get('IPSubnet'):
                    subnet_masks = re.findall(r'"([^"]+)"', config['IPSubnet'])
                    nic_info['subnet_masks'] = subnet_masks
            
            # 7. 优化网卡类型判断
            # 优先使用PhysicalAdapter字段，因为它更可靠
            if physical_adapter:
                nic_info['adapter_type'] = 'Physical'
            else:
                nic_info['adapter_type'] = 'Virtual'
            
            # 8. 判断有线网卡和无线网卡
            if nic_info['adapter_type'] == 'Physical':
                if is_wireless_nic(nic_info['index']):
                    nic_info['connection_type'] = 'Wireless'
                else:
                    nic_info['connection_type'] = 'Wired'
            
            nic_list.append(nic_info)
        
        # 9. 处理Win32_NetworkAdapterConfiguration信息（补充）
        for config in win32_nic_config_info:
            # 跳过无效数据
            mac_address = config.get('MACAddress', '')
            if not mac_address:
                continue
            
            # 跳过已经处理过的网卡
            mac_upper = mac_address.upper()
            if any(nic['mac_address'].upper() == mac_upper for nic in nic_list):
                continue
            
            # 获取网卡基本信息
            nic_info = {
                'guid': config.get('SettingID', ''),
                'mac_address': mac_address,
                'physical_address': mac_address,
                'index': config.get('Index', ''),
                'net_enabled': config.get('IPEnabled', '').upper() == 'TRUE',
                'physical_adapter': True,  # 默认处理为物理网卡
                'adapter_type': 'Physical',
                'connection_type': 'Unknown',
                'ip_addresses': [],
                'subnet_masks': [],
                'default_gateway': None,
                'dns_servers': []
            }
            
            # 解析IP地址
            if config.get('IPAddress'):
                ip_addresses = re.findall(r'"([^"]+)"', config['IPAddress'])
                nic_info['ip_addresses'] = ip_addresses
            # 解析子网掩码
            if config.get('IPSubnet'):
                subnet_masks = re.findall(r'"([^"]+)"', config['IPSubnet'])
                nic_info['subnet_masks'] = subnet_masks
            
            nic_list.append(nic_info)
        
        # 10. 对于没有IP地址的网卡，尝试从ipconfig获取
        if nic_list:
            ipconfig_output = self._run_cmd('ipconfig /all')
            
            # 按适配器分割输出
            adapter_blocks = ipconfig_output.split('\n\n')
            
            for block in adapter_blocks:
                if '适配器' not in block and 'Adapter' not in block:
                    continue
                
                # 解析物理地址
                mac_match = re.search(r'(?:物理地址|Physical Address)[.:\s]+([0-9A-Fa-f:-]+)', block)
                if mac_match:
                    mac = mac_match.group(1).upper().replace('-', ':')
                    # 查找对应的网卡
                    for nic in nic_list:
                        if nic['mac_address'].upper().replace('-', ':') == mac:
                            # 解析默认网关
                            gateway_match = re.search(r'(?:默认网关|Default Gateway)[.:\s]+([0-9.]+)', block)
                            if gateway_match:
                                nic['default_gateway'] = gateway_match.group(1)
                            # 解析DNS服务器
                            dns_matches = re.findall(r'(?:DNS 服务器|DNS Servers)[.:\s]+([0-9.]+)', block)
                            if dns_matches:
                                nic['dns_servers'] = dns_matches
                            break
        
        return nic_list
    
    def get_all_network_info(self):
        """获取所有网络信息"""
        return {
            "adapters": self.get_network_adapters(),
            "nic_info": self.get_nic_info(),
            "ip_addresses": self.get_ip_addresses(),
            "network_stats": self.get_network_stats(),
            "network_connections": self.get_network_connections(),
            "dns_servers": self.get_dns_servers(),
            "default_gateway": self.get_default_gateway(),
            "hostname": self.get_hostname(),
            "fqdn": self.get_fqdn(),
            "network_profiles": self.get_network_profiles(),
            "firewall_status": self.get_firewall_status()
        }
