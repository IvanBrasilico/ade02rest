import logging
import os
import pickle
import time

import six
from flask import request, jsonify, g, current_app
from jose import JWTError, jwt
from werkzeug.exceptions import Unauthorized

import assinador
from apiserver.api import _response
from apiserver.models.orm import ChavePublicaRecinto


def make_secret():
    try:
        with open('SECRET', 'rb') as secret:
            secret = pickle.load(secret)
    except (FileNotFoundError, pickle.PickleError):
        secret = os.urandom(24)
        with open('SECRET', 'wb') as out:
            pickle.dump(secret, out, pickle.HIGHEST_PROTOCOL)
    return secret


JWT_ISSUER = 'api-recintos'
JWT_SECRET = str(make_secret())
JWT_LIFETIME_SECONDS = 600
JWT_ALGORITHM = 'HS256'


def generate_token(recinto):
    timestamp = _current_timestamp()
    payload = {
        'iss': JWT_ISSUER,
        'iat': int(timestamp),
        'exp': int(timestamp + JWT_LIFETIME_SECONDS),
        'recinto': str(recinto['recinto']),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        logging.error(e, exc_info=True)
        six.raise_from(Unauthorized, e)


def get_secret(user, token_info) -> str:
    return """
    You are user_id {user} and the secret is 'wbevuec'.
    Decoded token claims: {token_info}.
    """.format(user=user, token_info=token_info)


def _current_timestamp() -> int:
    return int(time.time())


def valida_assinatura(request, db_session=None):
    token = request.headers.get('Authorization')
    if db_session is None:
        db_session = current_app.config['db_session']
    if token:
        token = token.split()
        if len(token) == 2:
            token = token[1]
        print(token)
        decoded_token = decode_token(token)
        if request.json and decoded_token and isinstance(decoded_token, dict):
            recinto = decoded_token.get('recinto')
            if g:
                g['recinto'] = recinto
            assinado = request.json.get('assinado')
            print('recinto: %s' % recinto)
            print('assinado: %s' % assinado)
            public_key_pem = ChavePublicaRecinto.get_public_key(db_session, recinto)
            public_key = assinador.load_public_key(public_key_pem)
            try:
                assinador.verify(assinado, recinto.encode('utf8'), public_key)
            except Exception as err:
                logging.error(err, exc_info=True)
                return False
    return True


def configure_signature(app):
    @app.before_request
    def before_request():
        if not valida_assinatura(request):
            return jsonify(_response('Assinatura inválida', 400)), 400
