import subprocess
import re

class HardwareInfo:
    """Windows硬件信息获取类，使用命令行工具获取硬件信息"""
    
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
    
    def get_cpu_info(self):
        """使用wmic获取CPU信息"""
        cpu_info = {
            "manufacturer": "",
            "model": "",
            "cores": 0,
            "threads": 0,
            "max_clock_speed": 0,
            "current_clock_speed": 0
        }
        
        # 获取CPU制造商和型号
        output = self._run_cmd('wmic cpu get manufacturer,name /value')
        lines = output.strip().split('\n')
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                if key.strip() == 'Manufacturer':
                    cpu_info['manufacturer'] = value.strip()
                elif key.strip() == 'Name':
                    cpu_info['model'] = value.strip()
        
        # 获取CPU核心数和线程数
        output = self._run_cmd('wmic cpu get NumberOfCores,NumberOfLogicalProcessors /value')
        lines = output.strip().split('\n')
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                if key.strip() == 'NumberOfCores':
                    cpu_info['cores'] = int(value.strip()) if value.strip() else 0
                elif key.strip() == 'NumberOfLogicalProcessors':
                    cpu_info['threads'] = int(value.strip()) if value.strip() else 0
        
        # 获取CPU频率
        output = self._run_cmd('wmic cpu get MaxClockSpeed,CurrentClockSpeed /value')
        lines = output.strip().split('\n')
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                if key.strip() == 'MaxClockSpeed':
                    cpu_info['max_clock_speed'] = int(value.strip()) if value.strip() else 0
                elif key.strip() == 'CurrentClockSpeed':
                    cpu_info['current_clock_speed'] = int(value.strip()) if value.strip() else 0
        
        return cpu_info
    
    def get_memory_info(self):
        """使用wmic获取内存信息"""
        memory_info = {
            "total": 0,
            "available": 0,
            "used": 0,
            "percent": 0
        }
        
        # 获取物理内存总量
        output = self._run_cmd('wmic computersystem get TotalPhysicalMemory /value')
        match = re.search(r'TotalPhysicalMemory=(\d+)', output)
        if match:
            memory_info['total'] = int(match.group(1))
        
        # 使用wmic获取可用内存
        output = self._run_cmd('wmic OS get FreePhysicalMemory /value')
        match = re.search(r'FreePhysicalMemory=(\d+)', output)
        if match:
            available_kb = int(match.group(1))
            available_bytes = available_kb * 1024
            memory_info['available'] = available_bytes
            memory_info['used'] = memory_info['total'] - available_bytes
            if memory_info['total'] > 0:
                memory_info['percent'] = round((memory_info['used'] / memory_info['total']) * 100, 1)
        
        return memory_info
    
    def get_disk_info(self):
        """使用wmic获取硬盘信息，仅返回固定硬盘，排除USB设备"""
        disks = []
        
        # 使用wmic获取所有磁盘驱动器
        output = self._run_cmd('wmic diskdrive get caption,size,interfacetype,name')
        
        # 处理wmic输出
        lines = output.strip().split('\n')
        if len(lines) < 2:
            return disks
        
        # 跳过标题行，处理数据行
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            # 从输出中可以看到，实际字段顺序是：Caption, InterfaceType, Name, Size
            # 使用更可靠的解析方式，处理没有size的情况
            # 首先查找InterfaceType，然后查找Name
            
            # 查找InterfaceType (IDE/SATA/USB等)
            interface_types = ['IDE', 'SATA', 'PCIe', 'USB', 'SCSI', 'SAS']
            interface_type = None
            for iface in interface_types:
                if f' {iface} ' in f' {line} ':
                    interface_type = iface
                    break
            
            if not interface_type:
                continue
            
            # 排除USB设备
            if interface_type == 'USB':
                continue
            
            # 查找Name (\\.\PHYSICALDRIVEX)
            name_start = line.find('\\.\\PHYSICALDRIVE')
            if name_start == -1:
                continue
            
            # 提取Caption (从开始到InterfaceType)
            caption = line[:line.find(f' {interface_type} ')].strip()
            
            # 提取Name (从PHYSICALDRIVE开始到行尾或下一个空格)
            name_end = line.find(' ', name_start)
            if name_end == -1:
                name = line[name_start:].strip()
            else:
                name = line[name_start:name_end].strip()
            
            # 提取Size (从Name之后到行尾)
            size_str = line[name_end:].strip() if name_end != -1 else ''
            size = int(size_str) if size_str and size_str.isdigit() else 0
            
            disks.append({
                "model": caption,
                "manufacturer": "",
                "size": size,
                "interface_type": interface_type,
                "name": name
            })
        
        return disks
    
    def get_partition_info(self):
        """使用wmic获取分区信息"""
        partitions = []
        
        output = self._run_cmd('wmic logicaldisk get deviceid,description,freespace,size,volumename /value')
        partition_sections = output.strip().split('\n\n')
        
        for section in partition_sections:
            if not section:
                continue
            
            partition = {
                "device": "",
                "mountpoint": "",
                "description": "",
                "total": 0,
                "free": 0,
                "used": 0,
                "percent": 0,
                "volume_name": ""
            }
            
            lines = section.split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'DeviceID':
                        partition['device'] = value
                        partition['mountpoint'] = value
                    elif key == 'Description':
                        partition['description'] = value
                    elif key == 'FreeSpace' and value:
                        partition['free'] = int(value)
                    elif key == 'Size' and value:
                        partition['total'] = int(value)
                    elif key == 'VolumeName':
                        partition['volume_name'] = value
            
            if partition['total'] > 0:
                partition['used'] = partition['total'] - partition['free']
                partition['percent'] = round((partition['used'] / partition['total']) * 100, 1)
            
            partitions.append(partition)
        
        return partitions
    
    def get_gpu_info(self):
        """使用wmic获取显卡信息"""
        gpus = []
        
        output = self._run_cmd('wmic path win32_VideoController get AdapterCompatibility,Name,AdapterRAM,DriverVersion /value')
        gpu_sections = output.strip().split('\n\n')
        
        for section in gpu_sections:
            if not section:
                continue
            
            gpu_info = {
                "manufacturer": "",
                "model": "",
                "vram": 0,
                "driver_version": ""
            }
            
            lines = section.split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'AdapterCompatibility':
                        gpu_info['manufacturer'] = value
                    elif key == 'Name':
                        gpu_info['model'] = value
                    elif key == 'AdapterRAM' and value:
                        gpu_info['vram'] = int(value)
                    elif key == 'DriverVersion':
                        gpu_info['driver_version'] = value
            
            gpus.append(gpu_info)
        
        return gpus
    
    def get_motherboard_info(self):
        """使用wmic获取主板信息"""
        motherboard_info = {
            "manufacturer": "",
            "model": "",
            "serial_number": ""
        }
        
        output = self._run_cmd('wmic baseboard get product,manufacturer,serialnumber /value')
        lines = output.strip().split('\n')
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'Manufacturer':
                    motherboard_info['manufacturer'] = value
                elif key == 'Product':
                    motherboard_info['model'] = value
                elif key == 'SerialNumber':
                    motherboard_info['serial_number'] = value
        
        return motherboard_info
    
    def get_network_adapters(self):
        """使用wmic获取网络适配器信息"""
        adapters = []
        
        output = self._run_cmd('wmic nic get name,manufacturer,macaddress,speed,netenabled /value')
        adapter_sections = output.strip().split('\n\n')
        
        for section in adapter_sections:
            if not section:
                continue
            
            adapter_info = {
                "name": "",
                "manufacturer": "",
                "mac_address": "",
                "speed": 0,
                "status": "Disabled"
            }
            
            lines = section.split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'Name':
                        adapter_info['name'] = value
                    elif key == 'Manufacturer':
                        adapter_info['manufacturer'] = value
                    elif key == 'MACAddress':
                        adapter_info['mac_address'] = value
                    elif key == 'Speed' and value:
                        adapter_info['speed'] = int(value)
                    elif key == 'NetEnabled' and value == 'TRUE':
                        adapter_info['status'] = "Enabled"
            
            if adapter_info['mac_address']:  # 只添加有MAC地址的适配器
                adapters.append(adapter_info)
        
        return adapters
    
    def get_bios_info(self):
        """使用wmic获取BIOS信息"""
        bios_info = {
            "manufacturer": "",
            "version": "",
            "release_date": "",
            "serial_number": ""
        }
        
        output = self._run_cmd('wmic bios get manufacturer,version,releasedate,serialnumber /value')
        lines = output.strip().split('\n')
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'Manufacturer':
                    bios_info['manufacturer'] = value
                elif key == 'Version':
                    bios_info['version'] = value
                elif key == 'ReleaseDate':
                    bios_info['release_date'] = value
                elif key == 'SerialNumber':
                    bios_info['serial_number'] = value
        
        return bios_info
    
    def get_usb_storage_info(self):
        """使用wmic获取USB存储设备信息"""
        usb_devices = []
        
        # 使用wmic获取所有磁盘驱动器，然后过滤出USB设备
        output = self._run_cmd('wmic diskdrive get caption,size,interfacetype,name,mediatype /value')
        
        # 处理输出，逐行解析，重新组织设备信息
        current_device = None
        lines = [line.strip() for line in output.strip().split('\n') if line.strip()]
        
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # 检查是否开始新的设备信息
                if key == 'Caption':
                    # 如果有当前设备且是USB设备，添加到列表
                    if current_device and current_device['interface_type'] == 'USB' and current_device['name']:
                        usb_devices.append(current_device)
                    # 创建新设备信息
                    current_device = {
                        "model": value,
                        "manufacturer": "",
                        "size": 0,
                        "interface_type": "",
                        "name": "",
                        "media_type": ""
                    }
                elif current_device:
                    # 解析当前设备的其他字段
                    if key == 'Size' and value:
                        current_device['size'] = int(value)
                    elif key == 'InterfaceType':
                        current_device['interface_type'] = value
                    elif key == 'Name':
                        current_device['name'] = value
                    elif key == 'MediaType':
                        current_device['media_type'] = value
        
        # 处理最后一个设备
        if current_device and current_device['interface_type'] == 'USB' and current_device['name']:
            usb_devices.append(current_device)
        
        return usb_devices
    
    def get_all_hardware_info(self):
        """获取所有硬件信息"""
        return {
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disks": self.get_disk_info(),
            "usb_devices": self.get_usb_storage_info(),
            "partitions": self.get_partition_info(),
            "gpus": self.get_gpu_info(),
            "motherboard": self.get_motherboard_info(),
            "network_adapters": self.get_network_adapters(),
            "bios": self.get_bios_info()
        }
