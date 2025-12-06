from setuptools import setup, find_packages

setup(
    name="avatar-ecosystem",
    version="1.0.0",
    author="Your Name",
    description="A comprehensive suite of modern Python GUI applications.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JedizLaPulga/Avatar",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Pillow",
        "opencv-python",
        "tkinterweb",
        "requests",
        "pygame"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'avatar-dashboard=apps.dashboard.main:main',
        ],
    },
)
