import struct

import constants
import exception


class Message:
    def __init__(self, type="", data=""):
        self.type = type
        self.data = data

    def __str__(self):
        type = struct.pack("!B", self.type)
        return type + self.data


class MessageParser:
    @staticmethod
    def __get_message_type(message):
        try:
            return constants.message_dictionary[ord(message[0])]
        except exception.TypeException as e:
            print str(e)

    def validate_message_type(self, message):
        try:
            if self.__get_message_type(message) not in constants.message_type:
                raise