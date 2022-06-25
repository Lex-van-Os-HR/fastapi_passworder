import base64
import secrets
import generators


class Passworder:
    DEFAULT_ALGO = "SHA512"
    ALGO_MAP = {
        "SHA512": generators.Sha512Generator,
        "SHA256": generators.Sha256Generator,
        "MD5": generators.MD5Generator,
    }

    def get_supported_algorithms(self):
        return list(self.ALGO_MAP)

    def get_linux_password(self, cleartext, salt=None, algorithm=None):
        password_digest = self.get_password_hash(cleartext, salt, algorithm)
        password_b64 = base64.b64encode(password_digest).decode()
        generator = self.ALGO_MAP[algorithm]
        linux_digest = f"${generator.linux_num}${salt}${password_b64}"
        return linux_digest

    def get_password_hash(self, cleartext, salt=None, algorithm=None):
        if not algorithm:
            algorithm = self.DEFAULT_ALGO
        if algorithm not in self.ALGO_MAP:
            raise ValueError(
                f"Incorrect algorithm, one\
                     of {', '.join(self.ALGO_MAP)} is required."
            )
        generator = self.ALGO_MAP[algorithm]()
        return generator.hash(cleartext, salt)

    def verify_password(self, password, hash_digest, salt=None,
                    algorithm=None):
        if not algorithm:
            algorithm = self.DEFAULT_ALGO
        hashed_pw = self.get_password_hash(password,salt=salt, 
                                           algorithm=algorithm)
        return secrets.compare_digest(hashed_pw, hash_digest)
