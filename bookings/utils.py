import qrcode
from io import BytesIO
from django.core.files import File
from cryptography.fernet import Fernet
from django.conf import settings


def encrypt_data(plain_text):
    key=settings.FERNET_KEY.encode()
    f=Fernet(key)
    token=f.encrypt(plain_text.encode())
    return token.decode()

def decrypt_data(token):
    key=settings.FERNET_KEY.encode()
    f=Fernet(key)
    decrypted=f.decrypt(token.encode())
    return decrypted.decode()

def generate_qr_code(text):
    qr=qrcode.make(text)
    buffer=BytesIO()
    qr.save(buffer,format='PNG')
    buffer.seek(0)
    return File(buffer,name='qr.png')