from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shadow_coding",
    version="3.3.1",  # 更新为最新版本号
    author="严俊皓",
    author_email="2857922968@qq.com",
    description="Shadow_Coding: The Secure Vibe-Coding Gateway - AI 代码隐私保护网关",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yjh2222332024/shadow_coding",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "requests>=2.31.0",
        "astunparse>=1.6.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "build>=1.0.0",
            "twine>=4.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "shadow_coding=shadow_coding_cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",  # 从 Alpha 升级到 Beta
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU Affero General Public License v3 (AGPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Software Development",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.8',
    project_urls={
        "Bug Reports": "https://github.com/yjh2222332024/shadow_coding/issues",
        "Source": "https://github.com/yjh2222332024/shadow_coding",
        "Documentation": "https://github.com/yjh2222332024/shadow_coding#readme",
    },
    keywords="security privacy ai code-obfuscation llama cursor",
)
