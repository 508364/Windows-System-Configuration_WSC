"""多语言支持模块"""

import gettext
import os
import sys
import locale
import ctypes

# 定义支持的语言列表
SUPPORTED_LANGUAGES = {
    'zh_CN': '中文',
    'en_US': 'English'
}

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
i18n_dir = os.path.join(current_dir, 'i18n')

def get_system_language():
    """获取系统主语言
    
    Returns:
        语言代码，如 'zh_CN' 或 'en_US'
    """
    try:
        # 尝试使用ctypes获取Windows系统语言
        if sys.platform == 'win32':
            # 获取系统区域设置
            windll = ctypes.windll.kernel32
            lang_id = windll.GetUserDefaultUILanguage()
            # 转换为语言代码
            lang_code = locale.windows_locale[lang_id]
            return lang_code
        else:
            # 非Windows系统使用locale
            return locale.getdefaultlocale()[0]
    except Exception:
        # 如果获取失败，默认使用中文
        return 'zh_CN'

def get_supported_language(lang_code):
    """获取支持的语言代码，如果不支持则返回默认语言
    
    Args:
        lang_code: 系统语言代码
        
    Returns:
        支持的语言代码
    """
    if lang_code in SUPPORTED_LANGUAGES:
        return lang_code
    # 检查语言前缀是否支持
    lang_prefix = lang_code.split('_')[0]
    for supported_lang in SUPPORTED_LANGUAGES:
        if supported_lang.startswith(lang_prefix):
            return supported_lang
    # 默认使用中文
    return 'zh_CN'

# 获取系统语言
system_lang = get_system_language()
supported_lang = get_supported_language(system_lang)

# 初始化翻译器
trans = gettext.translation(
    'wsc',
    localedir=i18n_dir,
    languages=[supported_lang],  # 使用系统主语言
    fallback=True
)

def _(message):
    """翻译函数
    
    Args:
        message: 需要翻译的消息
        
    Returns:
        翻译后的消息
    """
    return trans.gettext(message)

def set_language(language_code):
    """设置当前使用的语言
    
    Args:
        language_code: 语言代码，如 'zh_CN' 或 'en_US'
    """
    global trans
    
    if language_code in SUPPORTED_LANGUAGES:
        trans = gettext.translation(
            'wsc',
            localedir=i18n_dir,
            languages=[language_code],
            fallback=True
        )
    else:
        print(f"不支持的语言: {language_code}")
        print(f"支持的语言: {', '.join(SUPPORTED_LANGUAGES.keys())}")

def get_supported_languages():
    """获取支持的语言列表
    
    Returns:
        支持的语言字典
    """
    return SUPPORTED_LANGUAGES
