import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timetracker-raspberry-pi-francisco-revilla",
    version="0.0.1",
    author="Francisco Javier Revilla Linares",
    author_email="paconte@gmail.com",
    description="A fingerprint software to be run in a raspberry pi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paconte/timetracker",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: POSIX :: Linux",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
)