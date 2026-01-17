import subprocess
import re
import winreg
from .utils import read_registry_value

class SecurityInfo:
    """Windows安全信息获取类，使用命令行工具获取信息"""
    
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
    
    def get_user_accounts(self):
        """使用wmic获取用户账户列表"""
        accounts = []
        output = self._run_cmd('wmic useraccount get name,fullname,description,disabled,lockout,passwordrequired,sid /value')
        
        # 分割输出为账户块
        account_sections = output.strip().split('\n\n')
        
        for section in account_sections:
            if not section:
                continue
            
            account_info = {
                "name": "",
                "full_name": "",
                "description": "",
                "disabled": False,
                "lockout": False,
                "password_required": False,
                "sid": ""
            }
            
            lines = section.split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'Name':
                        account_info['name'] = value
                    elif key == 'FullName':
                        account_info['full_name'] = value
                    elif key == 'Description':
                        account_info['description'] = value
                    elif key == 'Disabled' and value == 'TRUE':
                        account_info['disabled'] = True
                    elif key == 'Lockout' and value == 'TRUE':
                        account_info['lockout'] = True
                    elif key == 'PasswordRequired' and value == 'TRUE':
                        account_info['password_required'] = True
                    elif key == 'SID':
                        account_info['sid'] = value
            
            if account_info['name']:  # 只添加有名称的账户
                accounts.append(account_info)
        
        return accounts
    
    def get_user_groups(self):
        """使用wmic获取用户组列表"""
        groups = []
        output = self._run_cmd('wmic group get name,description,sid,domain /value')
        
        # 分割输出为组块
        group_sections = output.strip().split('\n\n')
        
        for section in group_sections:
            if not section:
                continue
            
            group_info = {
                "name": "",
                "description": "",
                "sid": "",
                "domain": ""
            }
            
            lines = section.split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'Name':
                        group_info['name'] = value
                    elif key == 'Description':
                        group_info['description'] = value
                    elif key == 'SID':
                        group_info['sid'] = value
                    elif key == 'Domain':
                        group_info['domain'] = value
            
            if group_info['name']:  # 只添加有名称的组
                groups.append(group_info)
        
        return groups
    
    def get_group_members(self, group_name):
        """使用net localgroup获取特定组的成员列表
        
        Args:
            group_name: 组名称
            
        Returns:
            组成员列表
        """
        members = []
        output = self._run_cmd(f'net localgroup "{group_name}"')
        
        # 解析组成员
        lines = output.strip().split('\n')
        if len(lines) < 6:  # 跳过标题和空行
            return members
        
        # 成员列表从第6行开始，直到遇到空行或"命令成功完成"提示
        member_lines = lines[5:]
        for line in member_lines:
            line = line.strip()
            # 跳过空行、分隔线和命令成功提示
            if not line or line.startswith('-') or "命令成功完成" in line:
                continue
            members.append({
                "name": line,
                "domain": "",
                "account_type": "Win32_UserAccount"  # 默认假设为用户账户
            })
        
        return members
    
    def get_current_user(self):
        """使用whoami命令获取当前登录用户"""
        output = self._run_cmd('whoami')
        username = output.strip()
        if '\\' in username:
            domain, user = username.split('\\', 1)
            return {
                "username": username,
                "domain": domain
            }
        return {
            "username": username,
            "domain": ""
        }
    
    def get_current_user_sid(self):
        """使用wmic和whoami命令获取当前用户的用户名和SID"""
        # 使用whoami获取当前用户名
        current_user = self.get_current_user()
        username = current_user['username']
        
        # 提取用户名（去掉域名部分）
        if '\\' in username:
            _, user = username.split('\\', 1)
        else:
            user = username
        
        # 使用wmic获取所有用户的name和sid
        output = self._run_cmd('wmic useraccount get name,sid')
        
        # 解析输出，查找当前用户的SID
        lines = output.strip().split('\n')
        for line in lines[1:]:  # 跳过标题行
            line = line.strip()
            if not line:
                continue
            
            # 提取用户名和SID
            # 用户名和SID之间有多个空格分隔
            parts = line.split()
            if len(parts) >= 2:
                user_name = parts[0]
                sid = ' '.join(parts[1:])
                
                if user_name == user:
                    return {
                        "username": username,
                        "name": user,
                        "sid": sid,
                        "domain": current_user['domain']
                    }
        
        # 如果没有找到，返回基本信息
        return {
            "username": username,
            "name": user,
            "sid": "",
            "domain": current_user['domain']
        }
    
    def get_uac_settings(self):
        """获取UAC（用户账户控制）设置"""
        uac_reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        enable_lua = read_registry_value(uac_reg_path, "EnableLUA")
        consent_prompt_behavior_admin = read_registry_value(uac_reg_path, "ConsentPromptBehaviorAdmin")
        consent_prompt_behavior_user = read_registry_value(uac_reg_path, "ConsentPromptBehaviorUser")
        prompt_on_secure_desktop = read_registry_value(uac_reg_path, "PromptOnSecureDesktop")
        
        uac_levels = {
            0: "Never notify",
            1: "Notify only when apps try to make changes to my computer (do not dim my desktop)",
            2: "Notify only when apps try to make changes to my computer (dim my desktop)",
            3: "Always notify"
        }
        
        return {
            "enabled": bool(enable_lua),
            "admin_consent_behavior": uac_levels.get(consent_prompt_behavior_admin, "Unknown"),
            "user_consent_behavior": consent_prompt_behavior_user,
            "prompt_on_secure_desktop": bool(prompt_on_secure_desktop)
        }
    
    def get_windows_defender_status(self):
        """使用sc命令获取Windows Defender状态"""
        output = self._run_cmd('sc query WinDefend')
        
        status_match = re.search(r'STATE\s+: (.+)', output)
        start_type_match = re.search(r'START_TYPE\s+: (.+)', output)
        display_name_match = re.search(r'DISPLAY_NAME\s+: (.+)', output)
        
        return {
            "service_name": "WinDefend",
            "display_name": display_name_match.group(1) if display_name_match else "",
            "state": status_match.group(1) if status_match else "",
            "start_mode": start_type_match.group(1) if start_type_match else ""
        }
    
    def get_firewall_rules(self):
        """使用netsh advfirewall获取防火墙规则列表"""
        rules = []
        output = self._run_cmd('netsh advfirewall firewall show rule name=all')
        
        # 分割输出为规则块
        rule_sections = output.split('\n\n')
        
        for section in rule_sections:
            if 'Rule Name:' not in section:
                continue
            
            rule_info = {
                "name": "",
                "display_name": "",
                "description": "",
                "direction": "",
                "action": "",
                "enabled": False,
                "protocol": "",
                "local_ports": "",
                "remote_ports": "",
                "local_addresses": "",
                "remote_addresses": ""
            }
            
            # 解析规则名称
            name_match = re.search(r'Rule Name:\s+(.+)', section)
            if name_match:
                rule_info['name'] = name_match.group(1)
                rule_info['display_name'] = name_match.group(1)
            
            # 解析描述
            desc_match = re.search(r'Description:\s+(.+)', section)
            if desc_match:
                rule_info['description'] = desc_match.group(1)
            
            # 解析方向
            dir_match = re.search(r'Direction:\s+(.+)', section)
            if dir_match:
                rule_info['direction'] = dir_match.group(1)
            
            # 解析操作
            action_match = re.search(r'Action:\s+(.+)', section)
            if action_match:
                rule_info['action'] = action_match.group(1)
            
            # 解析启用状态
            enabled_match = re.search(r'Enabled:\s+(.+)', section)
            if enabled_match:
                rule_info['enabled'] = enabled_match.group(1).lower() == 'yes'
            
            # 解析协议
            protocol_match = re.search(r'Protocol:\s+(.+)', section)
            if protocol_match:
                rule_info['protocol'] = protocol_match.group(1)
            
            rules.append(rule_info)
        
        return rules
    
    def get_all_security_info(self):
        """获取所有安全信息"""
        return {
            "user_accounts": self.get_user_accounts(),
            "user_groups": self.get_user_groups(),
            "current_user": self.get_current_user(),
            "uac_settings": self.get_uac_settings(),
            "windows_defender_status": self.get_windows_defender_status(),
            "firewall_rules": self.get_firewall_rules()
        }
