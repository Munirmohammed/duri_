from setuptools import setup

packages = []
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()


setup(
    name="duri_api",
    version="0.0.1",
    description="user identity management",
    url="https://gitlab.com/omic/next/apis/duri",
    author="omic",
    author_email="support@omic.ai",
    license="MIT",
    include_package_data=True,
    install_requires=requirements,
    packages=packages,
    zip_safe=False
)
