from setuptools import setup, find_packages

setup(
    name="Windows-System-Configuration",
    version="0.1.0",
    author="508364",
    author_email="github508364@qq.com",
    description="Windows System Configuration (WSC) - A Python library for retrieving Windows system configuration and information",
    long_description="Windows System Configuration (WSC) is a comprehensive library to get detailed information about Windows systems, including hardware, software, network, and security configurations.",
    long_description_content_type="text/markdown",
    url="https://github.com/508364/Windows-System-Configuration_WSC",
    packages=find_packages(),
    install_requires=[
        # No external dependencies, uses only Python standard library and Windows built-in tools
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Hardware",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    # 添加缩写WSC作为控制台脚本入口点
    entry_points={
        "console_scripts": [
            "wsc=wsc:main",
        ],
    },
)
