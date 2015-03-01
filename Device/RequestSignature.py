"""
Simple signing mechanism
"""
import hashlib

class RequestSignature(object):
    """
    Simple signing mechanism
    """

    @staticmethod
    def __calculate_signature(params, salt):
        """
        Returns calculated signature from list of parameters and salt
        """
        signature = hashlib.sha256()

        for param in params:
            signature.update(param)

        signature.update(salt)

        return signature.hexdigest()

    @staticmethod
    def sign(params, salt):
        """
        Returns signature
        """
        return RequestSignature.__calculate_signature(params, salt)

    @staticmethod
    def check(params, salt, signature):
        """
        Validates signature
        """
        return signature == RequestSignature.__calculate_signature(params, salt)

if __name__ == "__main__":
    print RequestSignature.sign(["test1", "8.36"], "878911ba-bf76-11e4-9790-f51b4ef9ee8b")
