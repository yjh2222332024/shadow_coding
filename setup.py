from setuptools import setup, find_packages

setup(
    name="spinecode",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "requests>=2.31.0",
        "astunparse>=1.6.3",
    ],
    entry_points={
        "console_scripts": [
            "spinecode=spinecode_cli:main",
        ],
    },
    author="Vibe Architect",
    description="SpineCode: The Secure Vibe-Coding Gateway",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
