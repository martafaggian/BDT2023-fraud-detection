'''
This code provides a parser for transforming data from a source format to a target format using Apache Flink.
It consists of two main components: the Parser class and the SFDToTarget class.
The Parser class handles the conversion of data from a specified source format to a target format. It is
initialized with the source type, target type, and file paths for the source and target parser definitions.
The class provides methods to retrieve the target types, source types, and the query associated with the parser.
It also includes functions to convert types from a file and convert type strings to corresponding Flink types.

The SFDToTarget class performs the mapping from synthetic financial datasets (SFD) to the target format. It takes
cache configuration arguments as input. The class implements the map function, which maps the input record to the
target format. It utilizes a cache object to read and retrieve data during the mapping process. The transformed
record is returned in the target format. The class also provides a method to retrieve the query dictionary for
the target format.

Overall, this code facilitates the conversion of data from a specific source format (e.g., synthetic financial datasets) to a
target format. The Parser class handles the general conversion process, while the SFDToTarget class focuses on the
specific mapping for synthetic financial datasets to the target format.
'''
from __future__ import annotations
import json
from enum import Enum
from pyflink.datastream.functions import MapFunction
from pyflink.common.typeinfo import Types
from pyflink.common.types import Row
from app.infrastructure import Cache
from app.model import Transaction


class SourceTypes(str, Enum):
    SYNTHETIC_FINANCIAL_DATASETS = "synthetic_financial_datasets"
    TARGET = "target"


class Parser:
    '''
    The `Parser` class handles the conversion of data from a source format to a target format.

    :param source: The source type
    :type source: str
    :param target: The target type
    :type target: str
    :param source_parser_file_path: File path for the source parser definition
    :type source_parser_file_path: str
    :param target_parser_file_path: File path for the target parser definition
    :type target_parser_file_path: str

    '''
    def __init__(
        self,
        source: str,
        target: str,
        source_parser_file_path: str,
        target_parser_file_path: str,
    ):
        self._source_types = self.get_types(source_parser_file_path)
        self._target_types = self.get_types(target_parser_file_path)
        self._source = source
        self._target = target
        self._source = source
        self.query = None

        if self._source == SourceTypes.SYNTHETIC_FINANCIAL_DATASETS and self._target == SourceTypes.TARGET:
            self.parse = SFDToTarget
            self.set_query(SFDToTarget.get_query())
        else:
            raise NotImplementedError(f"Parser from {self._source} to {self._target} not implemented")

    def get_query(self):
        '''
        Get the query associated with the parser

        :return: The query dict
        '''
        return self.query

    def set_query(self, query):
        '''
        Set the query for the parser

        :param query: The query to set
        '''
        self.query = query

    def get_target_types(self):
        '''
        Get the target types.

        :return: The target types
        '''
        return self._target_types

    def get_source_types(self):
        '''
        Get the source types.

        :return: The source types
        '''
        return self._source_types

    @classmethod
    def get_types(cls, file: str):
        '''
        Read and convert the types from a file.

        :param file: The file path
        :type file: str
        :return The converted types
        '''
        with open(file) as f:
            types = json.load(f)
        converted = {}
        for k,v in types.items():
            converted[k] = cls.convert_types(v)
        return Types.ROW_NAMED(
            list(converted.keys()),
            list(converted.values())
        )

    @classmethod
    def convert_types(cls, type_str: str) -> Types:
        '''
        Convert type strings to corresponding Flink types.

        :param type_str: The type string
        :type param: type_str
        :return: The converted Flink type
        '''
        type_str = type_str.lower().strip()
        if type_str in ["string", "text"]:
            return Types.STRING()
        elif type_str in ["double"]:
            return Types.DOUBLE()
        elif type_str in ["boolean", "bool"]:
            return Types.BOOLEAN()
        elif type_str in ["int", "integer"]:
            return Types.INT()
        elif type_str in ["float"]:
            return Types.FLOAT()
        elif type_str in ["floattuple"]:
            return Types.TUPLE([Types.FLOAT(), Types.FLOAT()])
        elif type_str in ["date"]:
            return Types.SQL_DATE()
        else:
            raise Exception(f"Unknown type {type_str}")


class SFDToTarget(MapFunction):
    '''
    The `SFDToTarget` class performs the mapping from synthetic financial datasets (SFD) to the target format.

    :param cache_conf_args: Configuration arguments for the cache
    '''
    def __init__(self, cache_conf_args):
        super().__init__()
        self._cache_conf_args = cache_conf_args

    def map(self, record):
        '''
        Map the input record to the target format.

        :param record: The input record
        :return: The transformed record in the target format
        '''
        # Declaration must be internal due to Flink contraints!
        cache = Cache.from_conf(**self._cache_conf_args)
        #
        account = cache.read(record["nameOrig"], is_dict=True)
        counterparty_id = record["nameDest"]
        counterparty_type = None
        counterparty_isinternal = False
        if cache.key_exists(counterparty_id):
            counterparty = cache.read(record["nameDest"], is_dict=True)
            counterparty_id = counterparty["user_id"]
            counterparty_type = counterparty["type"]
            counterparty_isinternal = True
        #
        if float(record["oldbalanceOrg"]) > float(record["newbalanceOrig"]):
            direction = "inbound"
        else:
            direction = "outbound"
        #
        return Row(
            user_id = account["user_id"],
            account_id = record["nameOrig"],
            bank_id = account["bank_id"],
            balance_before = record["oldbalanceOrg"],
            balance_after = record["newbalanceOrig"],
            account_type = account["type"],
            counterparty_account_id = counterparty_id,
            counterparty_isinternal = counterparty_isinternal,
            counterparty_type = counterparty_type,
            counterparty_name = None,
            amount = record["amount"],
            direction = direction,
            status = "confirmed",
            source_location = None,
            is_fraud = None,
            fraud_confidence = None)

    @staticmethod
    def get_query():
        '''
        Get the query dictionary for the target format.

        :return: The query dictionary.
        '''
        query = Transaction.get_query_dict(auto_id=True)
        query.update({
            '"timestamp"' : 'toTimestamp(now())'
        })
        return query
