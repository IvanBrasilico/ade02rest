from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def save_keys(private_key, public_key):
    with open('private_key.pem', 'wb') as f:
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        f.write(pem)
    with open('public_key.pem', 'wb') as f:
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        f.write(pem)
    return True


def read_private_key():
    with open('private_key.pem', 'rb') as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )


def read_public_key():
    with open('public_key.pem', 'rb') as key_file:
        return serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
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


def verify(signature, message, public_key):
    public_key.verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


private_key = read_private_key()
public_key = read_public_key()

message = 'TESTE'.encode('utf-8')
print(message)
encrypted = encript(message, public_key)
print(encrypted)

print(decript(encrypted, private_key))


signature = sign(message, private_key)

verify(signature, message, public_key)