from setuptools import setup, find_packages

setup(
    name="shellweaver",
    version="2.0.0",
    description="Beautifully colored CLI for managing web shells in CTF competitions.",
    author="ShellWeaver Contributors",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "urllib3>=2.0.0",
        "rich>=13.7.0",
        "prompt_toolkit>=3.0.43",
    ],
    entry_points={
        "console_scripts": [
            "shellweaver=shellweaver.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
    ],
)
