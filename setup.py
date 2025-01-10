from setuptools import setup, find_packages

setup(
    name='chatgpt_selenium_automation',
    version='1.1',
    packages=find_packages(),
    install_requires=[
        'selenium>=4.9.0',
    ],
    entry_points={
        'console_scripts': [
            'review=chatgpt_selenium_automation.main:main',
        ],
    },
)
