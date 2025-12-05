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
    
    def get_all_network_info(self):
        """获取所有网络信息"""
        return {
            "adapters": self.get_network_adapters(),
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
