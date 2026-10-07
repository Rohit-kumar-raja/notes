from setuptools import find_packages, setup

package_name = "my_topic"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="rohit",
    maintainer_email="rohit.kumar@taikishaindia.com",
    description="TODO: Package description",
    license="TODO: License declaration",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "publisher_topic=my_topic.publisher_node:main",
            "subcriber_topic=my_topic.subcriber_node:main",
        ],
    },
)
