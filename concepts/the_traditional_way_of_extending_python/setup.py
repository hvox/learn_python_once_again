from setuptools import setup, Extension

setup(
    name="aboba",
    version="1.2.3",
    ext_modules=[Extension("aboba", ["aboba.c"])],
)
