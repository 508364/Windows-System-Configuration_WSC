import winreg
import datetime

def format_bytes(size_bytes):
    """格式化字节大小为可读单位
    
    Args:
        size_bytes: 字节大小
        
    Returns:
        格式化后的可读大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {size_names[i]}"

def format_timestamp(timestamp):
    """将时间戳转换为可读日期时间格式
    
    Args:
        timestamp: 时间戳（秒）
        
    Returns:
        格式化后的日期时间字符串
    """
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def read_registry_value(key_path, value_name, hkey=winreg.HKEY_LOCAL_MACHINE):
    """安全读取Windows注册表值
    
    Args:
        key_path: 注册表键路径
        value_name: 注册表值名称
        hkey: 根键，默认为HKEY_LOCAL_MACHINE
        
    Returns:
        注册表值，如果读取失败则返回None
    """
    try:
        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        return value
    except OSError:
        return None

def get_registry_subkeys(key_path, hkey=winreg.HKEY_LOCAL_MACHINE):
    """获取注册表子键列表
    
    Args:
        key_path: 注册表键路径
        hkey: 根键，默认为HKEY_LOCAL_MACHINE
        
    Returns:
        子键名称列表，如果读取失败则返回空列表
    """
    subkeys = []
    try:
        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
        i = 0
        while True:
            try:
                subkey = winreg.EnumKey(key, i)
                subkeys.append(subkey)
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except OSError:
        pass
    return subkeys

def get_registry_values(key_path, hkey=winreg.HKEY_LOCAL_MACHINE):
    """获取注册表键下所有值
    
    Args:
        key_path: 注册表键路径
        hkey: 根键，默认为HKEY_LOCAL_MACHINE
        
    Returns:
        包含所有值名称和数据的字典，如果读取失败则返回空字典
    """
    values = {}
    try:
        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
        i = 0
        while True:
            try:
                value_name, value_data, _ = winreg.EnumValue(key, i)
                values[value_name] = value_data
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except OSError:
        pass
    return values

def safe_int(value, default=0):
    """安全转换为整数
    
    Args:
        value: 要转换的值
        default: 转换失败时的默认值
        
    Returns:
        转换后的整数或默认值
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """安全转换为浮点数
    
    Args:
        value: 要转换的值
        default: 转换失败时的默认值
        
    Returns:
        转换后的浮点数或默认值
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def detect_encoding(data):
    """检测字符串的编码（仅使用Python标准库）
    
    Args:
        data: 要检测编码的数据
        
    Returns:
        检测到的编码名称，如果检测失败则返回'utf-8'
    """
    # 尝试常见编码，不使用第三方库
    common_encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'ascii']
    
    if isinstance(data, str):
        return 'utf-8'  # 字符串已经是UTF-8编码（在Python 3中）
    
    for encoding in common_encodings:
        try:
            data.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    
    return 'utf-8'


def safe_decode(data, encoding='gbk', fallback_encodings=['utf-8', 'latin-1']):
    """安全解码二进制数据
    
    Args:
        data: 要解码的二进制数据
        encoding: 首选编码
        fallback_encodings: 回退编码列表
        
    Returns:
        解码后的字符串
    """
    if isinstance(data, str):
        return data
    
    encodings = [encoding] + fallback_encodings
    for enc in encodings:
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    
    # 如果所有编码都失败，使用replace模式
    return data.decode(encoding, errors='replace')


def safe_encode(text, encoding='utf-8', fallback_encodings=['gbk', 'latin-1']):
    """安全编码字符串为二进制数据
    
    Args:
        text: 要编码的字符串
        encoding: 首选编码
        fallback_encodings: 回退编码列表
        
    Returns:
        编码后的二进制数据
    """
    if isinstance(text, bytes):
        return text
    
    encodings = [encoding] + fallback_encodings
    for enc in encodings:
        try:
            return text.encode(enc)
        except UnicodeEncodeError:
            continue
    
    # 如果所有编码都失败，使用replace模式
    return text.encode(encoding, errors='replace')


def convert_encoding(text, from_encoding='gbk', to_encoding='utf-8'):
    """转换字符串编码
    
    Args:
        text: 要转换的字符串
        from_encoding: 源编码
        to_encoding: 目标编码
        
    Returns:
        转换后的字符串
    """
    if isinstance(text, bytes):
        text = safe_decode(text, from_encoding)
    
    return safe_encode(text, to_encoding).decode(to_encoding)
