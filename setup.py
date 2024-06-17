from setuptools import setup

setup(
    name='veno',
    version='2.0.7',
    description='Multi-purpose text/code editor meant for easy and vast expandability.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='GPLv3',
    packages=['veno', 'veno.modules'],
    install_requires=['Pygments'], # and curses
    entry_points = {
        'console_scripts': ['veno=veno.veno:main'],
    }
)
