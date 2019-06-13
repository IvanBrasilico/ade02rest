from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa

PRIVATE_KEY = 'private_key.pem'
PUBLIC_KEY = 'public_key.pem'


def generate_keys():
    """Gera chaves aleatórias RSA 2048

    :return: private_key, public_key
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def private_bytes(private_key, senha: str = None):
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pem

def public_bytes(public_key):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem


def save_keys(private_key, public_key):
    with open(PRIVATE_KEY, 'wb') as f:
        pem = private_bytes(private_key)
        f.write(pem)
    with open(PUBLIC_KEY, 'wb') as f:
        pem = public_bytes(public_key)
        f.write(pem)
    return True


def load_private_key(pem):
    return serialization.load_pem_private_key(
        pem,
        password=None,
        backend=default_backend()
    )


def read_private_key():
    with open(PRIVATE_KEY, 'rb') as key_file:
        return load_private_key(
            key_file.read()
        )


def load_public_key(pem):
    return serialization.load_pem_public_key(
        pem,
        backend=default_backend()
    )


def read_public_key():
    with open(PUBLIC_KEY, 'rb') as key_file:
        return load_public_key(
            key_file.read()
        )


def encript(message, public_key):
    return public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def decript(encrypted, private_key):
    return private_key.decrypt(
        encrypted,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def sign(message, private_key):
    return private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


def verify(signed_message, message, public_key):
    """Retorna exceção se não for possível validar a assinatura"""
    public_key.verify(
        signed_message,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


if __name__ == '__main__':
    # TESTS
    if not os.path.exists(PRIVATE_KEY):
        save_keys(*generate_keys())
    private_key = read_private_key()
    public_key = read_public_key()
    message = 'TESTE'.encode('utf-8')
    print(message)
    encrypted = encript(message, public_key)
    print(encrypted)
    print(decript(encrypted, private_key))
    signature = sign(message, private_key)
    print(signature)
    print(verify(signature, message, public_key))
