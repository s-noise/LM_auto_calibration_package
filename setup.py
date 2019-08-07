import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LM_auto_calibration",
    version="1.0",
    packages=['LM_auto_calibration', 'nionswift_plugin.LM_auto_calibration'],
    author="Tobias Mittelbauer, Simon Schafler, Stefan Manuel Noisternig",
    author_email="",
    description="Extension for nionswift to automatically choose the pixel to µm scale"\
               +" of a registered video device using the matrix_vision_camera python package"\
               +" and serial signals from a Microcontroler (Arduino Uno Rev3)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License, version 3",
        "Operating System :: Linux",
    ],
    include_package_data=True,
    python_requires='~=3.6',
    install_requires=[
    'matrix_vision_camera',
    #'mv_utils',  # sub-package of matrix_vision_camera
    #'mv_camera', # sub-package of matrix_vision_camera
    'pyserial',
    'nionutils',
    ],
    license='GPLv3',
)

