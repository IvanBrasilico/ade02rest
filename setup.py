# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "api_recintos"
VERSION = "0.9"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["connexion",
            "requests",
            "sqlalchemy",
            "marshmallow"]

setup(
    name=NAME,
    version=VERSION,
    description="APIRecintos",
    author_email="ivan.brasilico@rfb.gov.br",
    url="",
    keywords=["Swagger", "APIRecintos"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'OpenAPI3.0.1': ['app/openapi.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['api_recintos=app.app:main']},
    long_description="""\
    API para prestação de informações sobre eventos de controle aduaneiro a cargo dos Redex, Recintos, Operadores Portuários e demais intervenientes em carga sobre controle aduaneiro.
    """
)

