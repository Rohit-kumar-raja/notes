import os
from glob import glob

from setuptools import find_packages, setup

package_name = "amr"


def get_data_files():
    data_files = [
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
        (os.path.join("share", package_name, "worlds"), glob("worlds/*.sdf")),
    ]
    # Recursively install all model files (model.config, model.sdf, meshes, etc.)
    for root, _dirs, files in os.walk("models"):
        if files:
            install_dir = os.path.join("share", package_name, root)
            file_paths = [os.path.join(root, f) for f in files]
            data_files.append((install_dir, file_paths))
    return data_files


setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=get_data_files(),
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="rohit",
    maintainer_email="rohit.kumar@taikishaindia.com",
    description="Autonomous Mobile Robot (AMR) simulation in factory environment with LiDAR and Camera",
    license="Apache-2.0",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "joy_viewer = amr.joy_viewer:main",
        ],
    },
)
