import setuptools

setuptools.setup(
    install_requires=open('requirements.txt').readlines(),
    version='0.1.0',
    name='st7565',
    packages=setuptools.find_packages(),
    package_data={'st7565': ['images/*']},
    entry_points={
        'console_scripts': [
            'stleds = st7565.cmd.stleds:main',
            'stdemo = st7565.cmd.stdemo:main',
        ],
    }
)
