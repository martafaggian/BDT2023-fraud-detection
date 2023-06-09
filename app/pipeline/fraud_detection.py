'''
The provided code implements a class called "FraudDetection" that extends the "MapFunction" class
from the pyflink.datastream.functions module. This class is designed to perform fraud detection
on a data stream.

'''

from pyflink.datastream.functions import MapFunction

class FraudDetection(MapFunction):
    def map(self, value):
        '''
        This method is called for each element in the input data stream. It applies the fraud
        detection logic to the element and returns the updated element with fraud-related
        information.

        :param value: The input data element
        :return: The updataed dat aelement with fraud-related information
        '''
        is_fraud, fraud_conf = self.compute_fraud(value)
        value["is_fraud"] = is_fraud
        value["fraud_confidence"] = fraud_conf
        return value

    def compute_fraud(self, record):
        '''
        This method computes the fraud status and confidence level for a given record.

        :param record: A data record on which fraud detection is performed.
        :return is_fraud: An int indicating whether the record is classified as fraud (1) or not (1)
        :return fraud_conf: A float representing the confidence level of the fraud detection result
        '''
        # Fraud detection :)
        # Pyflink ML should be easy to integrate:
        # https://nightlies.apache.org/flink/flink-ml-docs-master/docs/try-flink-ml/python/quick-start/
        if record["amount"] > 5000:
            is_fraud = 1
            fraud_conf = 1.0
        else:
            is_fraud = 0
            fraud_conf = 0.0
        return is_fraud, fraud_conf

