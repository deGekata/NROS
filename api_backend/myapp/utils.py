""" Utils module """
import random
import re
import string


class Utils:
    """ Class for utils """
    @staticmethod
    def random_string(length):
        """ Function that creates random string with specified length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    @staticmethod
    def is_email_valid(email):
        """ Function that validates email """
        reg_expression = r"[^@]+@[^@]+\.[^@]+"
        return re.match(reg_expression, email)
