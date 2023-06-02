import os
import json
from enum import Enum
from pyflink.common.typeinfo import Types

class Parser:
    def __init__(
        self,
        # source_name,
        # target_name,
        source_parser_file: str):
        with open(source_parser_file) as f:
            types = json.load(f)
        self.types = {}
        for k,v in types.items():
            self.types[k] = self.convert_types(v)
        self.types_info = Types.ROW_NAMED(
            list(self.types.keys()),
            list(self.types.values())
        )

    def get_types(self):
        return self.types_info

    @staticmethod
    def convert_types(type_str: str) -> Types:
        type_str = type_str.lower().strip()
        if type_str == "string" or type_str == "text":
            return Types.STRING()
        elif type_str == "double":
            return Types.DOUBLE()
        elif type_str == "boolean" or type_str == "bool":
            return Types.BOOLEAN()
        elif type_str == "int" or type_str == "integer":
            return Types.INT()
        elif type_str == "float":
            return Types.FLOAT()
        else:
            raise Exception(f"Unknown type {type_str}")

    # @staticmethod
    # def from_sfd_to_target(record):
        # import pdb
        # pdb.set_trace()
        # if record['timestamp'] is None:

