import os
import subprocess
import re
import winreg
from .utils import read_registry_value, get_registry_values, get_registry_subkeys

class ConfigurationInfo:
    """Windows系统配置信息获取类，使用命令行工具获取信息"""
    
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
    
    def get_environment_variables(self):
        """获取环境变量"""
        return dict(os.environ)
    
    def get_system_services(self):
        """使用sc命令获取系统服务列表"""
        services = []
        output = self._run_cmd('sc query state= all')
        
        # 分割输出为服务块
        service_blocks = output.split('\n\n')
        
        for block in service_blocks:
            if 'SERVICE_NAME:' not in block:
                continue
            
            service_info = {
                "name": "",
                "display_name": "",
                "description": "",
                "state": "",
                "start_mode": "",
                "path_name": "",
                "service_type": ""
            }
            
            # 解析服务名称
            name_match = re.search(r'SERVICE_NAME:\s+(.+)', block)
            if name_match:
                service_info['name'] = name_match.group(1)
            
            # 解析显示名称
            display_name_match = re.search(r'DISPLAY_NAME:\s+(.+)', block)
            if display_name_match:
                service_info['display_name'] = display_name_match.group(1)
            
            # 解析状态
            state_match = re.search(r'STATE\s+: (.+)', block)
            if state_match:
                service_info['state'] = state_match.group(1)
            
            # 获取服务详细信息
            if service_info['name']:
                detail_output = self._run_cmd(f'sc qc "{service_info["name"]}"')
                
                # 解析服务类型
                type_match = re.search(r'TYPE\s+: (.+)', detail_output)
                if type_match:
                    service_info['service_type'] = type_match.group(1)
                
                # 解析启动类型
                start_type_match = re.search(r'START_TYPE\s+: (.+)', detail_output)
                if start_type_match:
                    service_info['start_mode'] = start_type_match.group(1)
                
                # 解析路径名称
                path_match = re.search(r'BINARY_PATH_NAME\s+: (.+)', detail_output)
                if path_match:
                    service_info['path_name'] = path_match.group(1)
                
                # 解析描述
                desc_output = self._run_cmd(f'sc description "{service_info["name"]}"')
                desc_match = re.search(r'DESCRIPTION:\s+(.+)', desc_output)
                if desc_match:
                    service_info['description'] = desc_match.group(1)
            
            services.append(service_info)
        
        return services
    
    def get_service_status(self, service_name):
        """使用sc命令获取特定服务状态
        
        Args:
            service_name: 服务名称
            
        Returns:
            服务状态信息字典，如果服务不存在则返回None
        """
        output = self._run_cmd(f'sc query "{service_name}"')
        
        if 'FAILED' in output:
            return None
        
        # 解析服务名称
        name_match = re.search(r'SERVICE_NAME:\s+(.+)', output)
        # 解析显示名称
        display_name_match = re.search(r'DISPLAY_NAME:\s+(.+)', output)
        # 解析状态
        state_match = re.search(r'STATE\s+: (.+)', output)
        
        # 获取服务启动类型
        qc_output = self._run_cmd(f'sc qc "{service_name}"')
        start_mode_match = re.search(r'START_TYPE\s+: (.+)', qc_output)
        
        return {
            "name": name_match.group(1) if name_match else service_name,
            "display_name": display_name_match.group(1) if display_name_match else "",
            "state": state_match.group(1) if state_match else "",
            "start_mode": start_mode_match.group(1) if start_mode_match else ""
        }
    
    def get_startup_items(self):
        """获取启动项列表"""
        startup_items = []
        
        # 从注册表获取启动项
        startup_reg_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\RunOnce"
        ]
        
        for reg_path in startup_reg_paths:
            items = get_registry_values(reg_path)
            for name, path in items.items():
                startup_items.append({
                    "name": name,
                    "path": path,
                    "location": reg_path
                })
        
        return startup_items
    
    def get_power_plans(self):
        """使用powercfg命令获取电源计划列表"""
        power_plans = []
        output = self._run_cmd('powercfg /list')
        
        # 解析电源计划
        plan_matches = re.findall(r'\s*(\{[0-9a-fA-F-]+\})\s*(\*\s*)?(.+)', output)
        for guid, is_active, name in plan_matches:
            power_plans.append({
                "name": name.strip(),
                "description": "",
                "instance_id": guid,
                "is_active": bool(is_active)
            })
        
        return power_plans
    
    def get_current_power_plan(self):
        """使用powercfg命令获取当前电源计划"""
        output = self._run_cmd('powercfg /getactivescheme')
        
        # 解析当前电源计划
        current_match = re.search(r'\s*(\{[0-9a-fA-F-]+\})\s*(\*\s*)?(.+)', output)
        if current_match:
            guid, _, name = current_match.groups()
            return {
                "name": name.strip(),
                "description": "",
                "instance_id": guid
            }
        return None
    
    def get_windows_update_settings(self):
        """获取Windows更新设置"""
        # 从注册表读取Windows更新设置
        update_settings = {}
        
        # 检查Windows更新服务是否自动启动
        update_service = self.get_service_status("wuauserv")
        update_settings["service_start_mode"] = update_service["start_mode"] if update_service else "Unknown"
        
        # 读取Windows更新配置
        update_reg_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
        
        # 检查自动更新是否启用
        au_option = read_registry_value(update_reg_path, "AUOptions")
        if au_option is not None:
            au_modes = {
                1: "Never check for updates",
                2: "Check for updates but let me choose whether to download and install them",
                3: "Download updates but let me choose whether to install them",
                4: "Install updates automatically"
            }
            update_settings["auto_update_mode"] = au_modes.get(au_option, "Unknown")
        else:
            update_settings["auto_update_mode"] = "Not configured"
        
        return update_settings
    
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
            "level": uac_levels.get(consent_prompt_behavior_admin, "Unknown"),
            "consent_prompt_behavior_admin": consent_prompt_behavior_admin
        }
    
    def get_all_configuration(self):
        """获取所有系统配置信息"""
        return {
            "environment_variables": self.get_environment_variables(),
            "startup_items": self.get_startup_items(),
            "power_plans": self.get_power_plans(),
            "current_power_plan": self.get_current_power_plan(),
            "windows_update_settings": self.get_windows_update_settings(),
            "uac_settings": self.get_uac_settings()
        }
