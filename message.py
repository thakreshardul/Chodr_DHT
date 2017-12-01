import struct

import constants
import exception


class Message:
    def __init__(self, type="", data=""):
        self.type = type
        self.data = data


class MessageParser:
    @staticmethod
    def get_message_type(message):
        try:
            return constants.message_dictionary[message.type]
        except exception.TypeException as e:
            print str(e)

    def validate_message_type(self, message):
        try:
            if self.get_message_type(message) not in constants.message_type:
                raise exception.TypeException
        except exception.TypeException as e:
            print str(e)

    @staticmethod
    def extract_data(message):
        try:
            return message.data
        except exception.DataException as e:
            print str(e)

