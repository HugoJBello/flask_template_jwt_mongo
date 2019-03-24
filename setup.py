
from setuptools import find_packages, setup


setup(
    name='flaskr',
    version='1.0.0',
    license='BSD',
    maintainer='',
    maintainer_email='hjbello.wk@gmail.com',
    description='The basic blog server built in the Flask tutorial.',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask_restful'
    ],
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
    },
)
