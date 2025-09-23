from setuptools import setup, find_packages

setup(
    name="gpu_settings",
    version="0.2",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "PyQt6",
        "PyQt6-Charts"
        "psutil"
    ],
    entry_points={
        "console_scripts": [
            "gpu-settings = gpu_settings.main:main",
        ],
    },
    author="A. M Samdani Mozumder",
    author_email="bsse1412@iit.du.ac.bd",
    description="GUI tool to manage GPUs",
    long_description="GPU Settings GUI application for Linux",
    long_description_content_type="text/plain",
)
