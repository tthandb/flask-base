from passlib.hash import pbkdf2_sha256


def hash_password(password):
    return pbkdf2_sha256.hash(password)


def verify_password(password, password_digest):
    try:
        return pbkdf2_sha256.verify(password, password_digest)
    except (ValueError, TypeError):
        return False
