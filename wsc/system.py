import platform
import os
import socket
import subprocess
import re
import time

class SystemInfo:
    """Windows系统基本信息获取类，减少第三方库依赖"""
    
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
    
    def get_os_version(self):
        """获取操作系统版本"""
        return platform.version()
    
    def get_os_name(self):
        """获取操作系统名称"""
        return platform.system() + " " + platform.release()
    
    def get_os_build(self):
        """使用wmic获取操作系统构建号"""
        output = self._run_cmd('wmic os get buildnumber /value')
        match = re.search(r'BuildNumber=(\d+)', output)
        if match:
            return match.group(1)
        return ""
    
    def get_service_pack(self):
        """使用wmic获取服务包信息"""
        output = self._run_cmd('wmic os get servicepackmajorversion /value')
        match = re.search(r'ServicePackMajorVersion=(\d+)', output)
        if match:
            return int(match.group(1))
        return 0
    
    def get_system_architecture(self):
        """获取系统架构 (32位/64位)"""
        return platform.architecture()[0]
    
    def get_boot_time(self):
        """使用wmic获取系统启动时间"""
        output = self._run_cmd('wmic os get lastbootuptime /value')
        match = re.search(r'LastBootUpTime=(\d{8})(\d{6})', output)
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            # 格式转换：YYYYMMDDHHMMSS -> 时间戳
            dt_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
            boot_time = time.mktime(time.strptime(dt_str, "%Y-%m-%d %H:%M:%S"))
            return boot_time
        return time.time()
    
    def get_computer_name(self):
        """获取计算机名称"""
        return socket.gethostname()
    
    def get_domain_name(self):
        """获取域名"""
        output = self._run_cmd('wmic computersystem get domain /value')
        match = re.search(r'Domain=(.+)', output)
        if match:
            domain = match.group(1).strip()
            # 如果是工作组，返回WORKGROUP
            if domain == socket.gethostname():
                return "WORKGROUP"
            return domain
        return "WORKGROUP"
    
    def get_system_directory(self):
        """获取系统目录"""
        return os.environ.get("SystemRoot", "C:\\Windows")
    
    def get_temp_directory(self):
        """获取临时目录"""
        return os.environ.get("TEMP", "C:\\Windows\\Temp")
    
    def get_all_info(self):
        """获取所有系统基本信息"""
        return {
            "os_name": self.get_os_name(),
            "os_version": self.get_os_version(),
            "os_build": self.get_os_build(),
            "service_pack": self.get_service_pack(),
            "architecture": self.get_system_architecture(),
            "boot_time": self.get_boot_time(),
            "computer_name": self.get_computer_name(),
            "domain_name": self.get_domain_name(),
            "system_directory": self.get_system_directory(),
            "temp_directory": self.get_temp_directory()
        }
