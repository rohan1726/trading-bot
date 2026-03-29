from setuptools import setup, find_packages

setup(
    name="trading-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "trading-bot=bot.cli:run",
        ],
    },
)
