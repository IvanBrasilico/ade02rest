"""Script de linha de comando para validar JSON de Eventos.

Script de linha de comando para validar ou enviar JSON de Eventos

Args:

    --dir: diretório a processar (caso queira gerar)
    --arquivo:
    --send: endereço do Servidor APIRecintos

"""
import json
import os

import click
import requests

from apiserver.models import orm
from apiserver.use_cases.usecases import UseCases

BASE_DIR = os.getcwd()
IMAGE_DIR = 'images'
API_URL = 'http://localhost:8000/'


@click.command()
@click.option('--dir', default=IMAGE_DIR,
              help='diretório a processar - padrão %s ' % IMAGE_DIR)
@click.option('--file', required=True,
              help='Arquivo a validar ou enviar')
@click.option('--send',
              help='URL do Servidor para envio')
def carrega(dir, file, send):
    """Script de linha de comando para integração do arquivo XML."""
    with open(os.path.join(BASE_DIR, file), 'r') as json_in:
        testes = json.load(json_in)
    if send:
        # request...
        requests.post(send + 'set_eventos', files={'file': (testes.read(), file)})
    else:  # Valida arquivo json com BD na memória
        print('Creating memory database')
        session, engine = orm.init_db('sqlite:///:memory:')
        orm.Base.metadata.create_all(bind=engine)
        usecases = UseCases(session, 'TESTE', 'localhost', '.')
        for classe, eventos in testes.items():
            print(classe)
            aclass = getattr(orm, classe)
            if isinstance(eventos, list):
                for evento in eventos:
                    result = usecases.insert_evento(aclass, evento)
                    print(result, result.IDEvento, result.hash)
            else:
                try:
                    result = usecases.insert_evento(aclass, eventos)
                    print(result, result.IDEvento, result.hash)
                except Exception as err:
                    print('Evento tipo: %s Linha do Evento: %s ERRO: %s' %
                          (classe, str(eventos)[:100], str(err)))


if __name__ == '__main__':
    carrega()
