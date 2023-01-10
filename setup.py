import setuptools

# from src.artosyntools import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='artosyntools',
    version='0.0.1',  # __version__,
    test_requires=[],
    url='https://github.com/ririyeye/artosyntools.git',
    license='MIT',
    author='ririyeye',
    author_email='200610237@qq.com',
    description='artosyn test tools',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: chinese',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        "Operating System :: OS Independent"
    ],
    keywords='python asyncio artosyn',
    python_requires='>=3.11',
    zip_safe=False,
    install_requires=[
        "asyncio",
        "aiohttp",
        "asyncssh",
        "aioftp"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src")
)
