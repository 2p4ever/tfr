#core/crypto.py
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from .consts import SALT_SIZE
import secrets
# -----------------------------------------------------------------------------
# ECDH
# -----------------------------------------------------------------------------
def ecdh_generate_key_pair():
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key
def ecdh_get_public_bytes(public_key):
    return public_key.public_bytes_raw()
def ecdh_load_public_bytes(pub_bytes):
    try:
        return x25519.X25519PublicKey.from_public_bytes(pub_bytes)
    except ValueError:
        raise ValueError("invalid public key bytes")
def ecdh_derive_aes_key(private_key, peer_public_key, salt: bytes, info=b"frame-v1"):
    if len(salt) < 16:
        raise ValueError("salt too short")
    try:
        shared = private_key.exchange(peer_public_key)
    except ValueError:
        raise ValueError("ECDH exchange failed")
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=info,
    )
    return hkdf.derive(shared)
def generate_salt():
    return secrets.token_bytes(SALT_SIZE)
# -----------------------------------------------------------------------------
# AES-GCM
# -----------------------------------------------------------------------------
def aes_gcm_encrypt(aes_key: bytes, data: bytes, ad: bytes = b"") -> bytes:
    aes_gcm = AESGCM(aes_key)
    nonce = secrets.token_bytes(12)
    ct = aes_gcm.encrypt(nonce, data, ad)
    return nonce + ct
def aes_gcm_decrypt(aes_key: bytes, encrypted: bytes, ad: bytes = b"") -> bytes:
    if len(encrypted) < 12:
        raise ValueError("aes_gcm: invalid data")
    aes_gcm = AESGCM(aes_key)
    nonce = encrypted[:12]
    ct = encrypted[12:]
    try:
        return aes_gcm.decrypt(nonce, ct, ad)
    except:
        raise ValueError("aes_gcm: decrypt failed")
# -----------------------------------------------------------------------------
# ChaCha20-Poly1305
# -----------------------------------------------------------------------------
def chacha20_poly1305_encrypt(chacha_key: bytes, data: bytes, ad: bytes = b"") -> bytes:
    chacha20_poly1305 = ChaCha20Poly1305(chacha_key)
    nonce = secrets.token_bytes(12)
    ct = chacha20_poly1305.encrypt(nonce, data, ad)
    return nonce + ct
def chacha20_poly1305_decrypt(chacha_key: bytes, encrypted: bytes, ad: bytes = b"") -> bytes:
    if len(encrypted) < 12:
        raise ValueError("chacha20_poly1305: invalid data")
    chacha20_poly1305 = ChaCha20Poly1305(chacha_key)
    nonce = encrypted[:12]
    ct = encrypted[12:]
    try:
        return chacha20_poly1305.decrypt(nonce, ct, ad)
    except:
        raise ValueError("chacha20_poly1305: decrypt failed")
