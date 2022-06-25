from passworder import Passworder
from random_password import get_random_password, get_random_salt
import unittest
from unittest import TestCase
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


class TestRandomPassword(TestCase):
    def test_random_password(self):
        random_pass = get_random_password()
        assert len(random_pass) > 0


class TestPassWorder(TestCase):
    def setUp(self):
        self.passworder = Passworder()

    def test_get_password_hash(self):
        random_password = get_random_password()
        random_hash2 = self.passworder.get_password_hash(
            cleartext=random_password)
        self.assertTrue(self.passworder.verify_password(
            random_password, random_hash2))

    def test_get_password_hash_salt(self):
        random_password = get_random_password()
        random_salt = get_random_salt()
        random_hash2 = self.passworder.get_password_hash(
            cleartext=random_password, salt=random_salt
        )
        self.assertTrue(
            self.passworder.verify_password(
                random_password, random_hash2, random_salt)
        )

    def test_generators(self):
        random_password = get_random_password()
        for algo in self.passworder.ALGO_MAP.keys():
            random_hash2 = self.passworder.get_password_hash(
                cleartext=random_password, algorithm=algo
            )
            self.assertTrue(
                self.passworder.verify_password(
                    random_password, random_hash2, algorithm=algo
                )
            )


if __name__ == "__main__":
    unittest.main()
