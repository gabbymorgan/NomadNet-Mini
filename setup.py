import setuptools

exec(open("nomadnet/_version.py", "r").read())

with open("README.md", "r") as fh:
    long_description = fh.read()

package_data = {
"": [
    "examples/messageboard/*",
    "ui/epaperui/assets/*",
    "ui/epaperui/assets/fonts/*"
    ]
}

setuptools.setup(
    name="nomadnet",
    version=__version__,
    author="Mark Qvist",
    author_email="mark@unsigned.io",
    description="Communicate Freely",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/markqvist/nomadnet",
    packages=setuptools.find_packages(),
    package_data=package_data,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points= {
        'console_scripts': ['nomadnet=nomadnet.nomadnet:main']
    },
    install_requires=["rns>=0.9.6", "lxmf>=0.7.1", "urwid>=2.6.16", "qrcode", "gpiozero", "smbus", "spidev", "lgpio", "numpy", "pillow", "arrow", "readchar"],
    python_requires=">=3.7",
)
