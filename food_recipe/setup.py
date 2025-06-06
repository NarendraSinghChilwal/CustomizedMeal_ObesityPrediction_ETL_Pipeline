from setuptools import find_packages, setup

setup(
    name="food_recipe",
    packages=find_packages(exclude=["food_recipe_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
