import logging
import os
import pickle
import time

import six
from flask import request, jsonify, current_app
from jose import JWTError, jwt
from werkzeug.exceptions import Unauthorized

from apiserver.api import _response
from assinador import read_public_key, verify


def make_secret():
    try:
        with open('SECRET', 'rb') as secret:
            secret = pickle.load(secret)
    except (FileNotFoundError, pickle.PickleError):
        secret = os.urandom(24)
        with open('SECRET', 'wb') as out:
            pickle.dump(secret, out, pickle.HIGHEST_PROTOCOL)
    return secret


JWT_ISSUER = 'com.zalando.connexion'
JWT_SECRET = make_secret()
JWT_LIFETIME_SECONDS = 600
JWT_ALGORITHM = 'HS256'


def generate_token(recinto):
    timestamp = _current_timestamp()
    payload = {
        'iss': JWT_ISSUER,
        'iat': int(timestamp),
        'exp': int(timestamp + JWT_LIFETIME_SECONDS),
        'sub': str(recinto['recinto']),
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


def valida_assinatura(request):
    token = request.headers.get('Authorization')
    if token:
        token = token.split()
        if len(token) == 2:
            token = token[1]
        decoded_token = decode_token(token)
        if request.json and decoded_token and isinstance(decoded_token, dict):
            recinto = decoded_token.get('sub')
            current_app.config['recinto'] = recinto
            assinado = request.json.get('assinado')
            public_key = read_public_key()
            try:
                verify(assinado, recinto, public_key)
                # TODO: Usar assinador para selecionar chave
            except Exception as err:
                logging.error(err, exc_info=True)
                return False
    return True


def configure_signature(app):
    @app.before_request
    def before_request():
        if not valida_assinatura(request):
            return jsonify(_response('Assinatura inválida', 400)), 400
