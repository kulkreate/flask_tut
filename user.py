from flask_login import UserMixin
import json
class User(UserMixin):
    """
    This is the Class witch provides the User structure.
    """
    def __init__(self, email: str, passwort: bytearray, role: str, salt: bytes):
        """
        This is the constructor of the User class.

        Paramters:
            email (string): The email of the user.
            password (bytearray): The passoword of the user.
            role (string): The role of the user (admin or user).
            salt (bytes): The password salt.
        """

        self.email = email
        self.passwort = passwort
        self.role = role
        self.salt = salt

        
    def __eq__(self, other):
        """
        Method to compare two users.

        Returns:
            boolean: True if the instances are equal, and False if not.
        """

        if isinstance(other, User):
            return self.email == other.email and self.passwort == other.passwort and self.role == other.role and self.salt == other.salt
        return False

    def __ne__(self, other):
        """
        Method to compare two users.

        Returns:
            boolean: False if the two entries are equal, and True if not.
        """

        return not self.__eq__(other)

    def serialize(self):
        return {
            self.email: {
                'role': self.role
            }
        }
    def get_id(self):
        """
        Method to get the ID of a user

        Returns:
            u'string: Encoded email
        """
        try:
            return self.email.encode(encoding='UTF-8')
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')
