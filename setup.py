from setuptools import setup

setup(
    name="timelog",
    version="0.1",
    py_modules=["main", "db", "helpers"],
    install_requires=["typer", "sqlalchemy", "pytz", "rich", "pytest", "pytest-mock"],
    entry_points={
        "console_scripts": ["timelog=main:app"],
    },
)
