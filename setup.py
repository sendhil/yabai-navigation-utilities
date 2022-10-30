from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='yabai_navigation_utilities',
    packages=find_packages(),
    version='0.0.11',
    description='Collection of scripts to make navigating Yabai easier.',
    author='Sendhil Panchadsaram',
    license='MIT',
    long_description=
    "A set of utilities to make navigating around Yabai(https://github.com/koekeishiya/yabai) easier. Details at https://github.com/sendhil/yabai-navigation-utilities.",
    install_requires=['click==8.1.3'],
    setup_requires=[],
    tests_require=[],
    test_suite='',
    py_modules=['yabai_navigation_utilities'],
    project_urls={
        'GitHub': 'https://github.com/sendhil/yabai-navigation-utilities',
    },
    entry_points='''
        [console_scripts]
        yabai-navigation-utilities=yabai_navigation_utilities.cli:main
    ''')
