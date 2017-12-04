#!/usr/bin/env python

import pickle

import constants
import exception


class Message:
    def __init__(self, msg_type=None, address=None, data=None, destination=None):
        self.type = msg_type
        self.sender = address
        self.data = data
        self.destination = destination


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

    # def extract_data(self, msg):
    #     return pickle.loads(msg.data)

    @staticmethod
    def pack_msg(msg):
        return pickle.dumps(msg)

    @staticmethod
    def unpack_msg(msg):
        try:
            msg = pickle.loads(msg)
            return msg
        except Exception as e:
            print str(e)

