import subprocess
import re
from .utils import get_registry_subkeys, get_registry_values

class SoftwareInfo:
    """Windows软件信息获取类，使用命令行工具获取信息"""
    
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
    
    def get_installed_programs(self):
        """获取已安装程序列表"""
        programs = []
        
        # 从注册表获取已安装程序
        reg_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        for reg_path in reg_paths:
            subkeys = get_registry_subkeys(reg_path)
            for subkey in subkeys:
                program_key = f"{reg_path}\\{subkey}"
                program_info = get_registry_values(program_key)
                
                # 过滤掉空的或系统组件
                if not program_info or "DisplayName" not in program_info:
                    continue
                
                program = {
                    "name": program_info.get("DisplayName", ""),
                    "version": program_info.get("DisplayVersion", ""),
                    "publisher": program_info.get("Publisher", ""),
                    "install_date": program_info.get("InstallDate", ""),
                    "uninstall_string": program_info.get("UninstallString", ""),
                    "install_location": program_info.get("InstallLocation", "")
                }
                programs.append(program)
        
        # 去重，按程序名称排序
        seen = set()
        unique_programs = []
        for program in programs:
            if program["name"] not in seen:
                seen.add(program["name"])
                unique_programs.append(program)
        
        return sorted(unique_programs, key=lambda x: x["name"])
    
    def get_running_processes(self):
        """使用tasklist命令获取正在运行的进程列表"""
        processes = []
        # 使用更简单的tasklist命令，不带详细信息，提高性能
        output = self._run_cmd('tasklist')
        lines = output.strip().split('\n')
        
        # 跳过标题行和分隔行
        if len(lines) >= 3:
            lines = lines[3:]
        
        for line in lines:
            if not line.strip():
                continue
            
            # 解析进程信息（使用空格分割，但要注意进程名称可能包含空格）
            # 格式：进程名  PID  会话名  会话#  内存使用
            # 我们使用正则表达式来匹配
            match = re.search(r'^([^\s]+\s*[^\s]+)\s+(\d+)\s+([^\s]+)\s+(\d+)\s+([^\s]+)', line)
            if match:
                name = match.group(1).strip()
                pid = int(match.group(2))
                session_name = match.group(3)
                session_number = match.group(4)
                mem_usage = match.group(5)
                
                processes.append({
                    "pid": pid,
                    "name": name,
                    "username": "",
                    "status": "",
                    "mem_usage": mem_usage,
                    "session_name": session_name,
                    "session_number": session_number,
                    "cpu_time": "",
                    "window_title": ""
                })
        
        return processes
    
    def get_process_info(self, pid):
        """使用tasklist命令获取特定进程信息
        
        Args:
            pid: 进程ID
            
        Returns:
            进程信息字典，如果进程不存在则返回None
        """
        output = self._run_cmd(f'tasklist /FI "PID eq {pid}" /FO CSV /V')
        lines = output.strip().split('\n')
        
        if len(lines) < 2:  # 标题行 + 至少一行进程信息
            return None
        
        # 解析进程信息
        line = lines[1]
        match = re.match(r'"([^"]*)","([^"]*)","([^"]*)","([^"]*)","([^"]*)","([^"]*)","([^"]*)","([^"]*)","([^"]*)","([^"]*)","([^"]*)"', line)
        if match:
            image_name = match.group(1)
            username = match.group(7)
            status = match.group(6)
            mem_usage = match.group(5)
            cpu_time = match.group(8)
            window_title = match.group(9)
            
            return {
                "pid": pid,
                "name": image_name,
                "username": username,
                "status": status,
                "mem_usage": mem_usage,
                "cpu_time": cpu_time,
                "window_title": window_title
            }
        return None
    
    def get_installed_drivers(self):
        """使用wmic获取已安装驱动程序列表"""
        drivers = []
        output = self._run_cmd('wmic sysdriver get name,displayname,description,state,startmode,pathname,servicetype /value')
        driver_sections = output.strip().split('\n\n')
        
        for section in driver_sections:
            if not section:
                continue
            
            driver_info = {
                "name": "",
                "display_name": "",
                "description": "",
                "state": "",
                "start_mode": "",
                "path_name": "",
                "driver_type": ""
            }
            
            lines = section.split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'Name':
                        driver_info['name'] = value
                    elif key == 'DisplayName':
                        driver_info['display_name'] = value
                    elif key == 'Description':
                        driver_info['description'] = value
                    elif key == 'State':
                        driver_info['state'] = value
                    elif key == 'StartMode':
                        driver_info['start_mode'] = value
                    elif key == 'PathName':
                        driver_info['path_name'] = value
                    elif key == 'ServiceType':
                        driver_info['driver_type'] = value
            
            drivers.append(driver_info)
        
        return drivers
    
    def get_driver_info(self, driver_name):
        """使用wmic获取特定驱动程序信息
        
        Args:
            driver_name: 驱动程序名称
            
        Returns:
            驱动程序信息字典，如果驱动不存在则返回None
        """
        output = self._run_cmd(f'wmic sysdriver where name="{driver_name}" get name,displayname,description,state,startmode /value')
        
        driver_info = {
            "name": "",
            "display_name": "",
            "description": "",
            "state": "",
            "start_mode": ""
        }
        
        lines = output.strip().split('\n')
        if not lines or len(lines) < 2:  # 至少需要两行输出（标题和内容）
            return None
        
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'Name':
                    driver_info['name'] = value
                elif key == 'DisplayName':
                    driver_info['display_name'] = value
                elif key == 'Description':
                    driver_info['description'] = value
                elif key == 'State':
                    driver_info['state'] = value
                elif key == 'StartMode':
                    driver_info['start_mode'] = value
        
        return driver_info if driver_info['name'] else None
    
    def get_startup_programs(self):
        """使用wmic获取启动程序列表"""
        startup_programs = []
        output = self._run_cmd('wmic startupcommand get caption,command,location,user /value')
        startup_sections = output.strip().split('\n\n')
        
        for section in startup_sections:
            if not section:
                continue
            
            startup_info = {
                "name": "",
                "command": "",
                "location": "",
                "user": ""
            }
            
            lines = section.split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'Caption':
                        startup_info['name'] = value
                    elif key == 'Command':
                        startup_info['command'] = value
                    elif key == 'Location':
                        startup_info['location'] = value
                    elif key == 'User':
                        startup_info['user'] = value
            
            if startup_info['name']:  # 只添加有名称的启动项
                startup_programs.append(startup_info)
        
        return startup_programs
    
    def get_windows_features(self):
        """使用dism命令获取Windows功能列表"""
        features = []
        
        # 使用dism命令获取Windows功能
        output = self._run_cmd('dism /online /get-features /format:table')
        lines = output.strip().split('\n')
        
        # 跳过标题行和空行
        feature_lines = [line for line in lines if '|' in line and 'Feature Name' not in line]
        
        for line in feature_lines:
            # 解析表格格式的输出
            parts = [part.strip() for part in line.split('|') if part.strip()]
            if len(parts) >= 2:
                feature_name = parts[0]
                state = parts[1]
                features.append({
                    "name": feature_name,
                    "state": state,
                    "installed": state == "Enabled"
                })
        
        return features
    
    def get_all_software_info(self):
        """获取所有软件信息"""
        return {
            "installed_programs": self.get_installed_programs(),
            "running_processes": self.get_running_processes(),
            "installed_drivers": self.get_installed_drivers(),
            "startup_programs": self.get_startup_programs(),
            "windows_features": self.get_windows_features()
        }
