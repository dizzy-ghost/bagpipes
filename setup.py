import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bagpipes", # Replace with your own username
    version="0.0.1",
    author='Dmitry "Dizzy" Povarov',
    author_email="dizzy@dizzy.tech",
    description="Named pipes in a bag",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dizzy-ghost/bagpipes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL3 License",
        "Operating System :: Linux",
    ]
)