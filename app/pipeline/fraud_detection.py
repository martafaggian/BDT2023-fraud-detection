'''
The provided code implements a fraud detection logic using the Flink DataStream API. It defines a
FraudDetection class that extends the MapFunction class. The map method of this class applies the
fraud detection algorithm to each element in the input data stream, updating the element with
fraud-related information. The compute_fraud method computes the fraud status and confidence level
for a given record. If the record's "amount" field is greater than 5000, it is classified as fraud
with a confidence level of 1.0; otherwise, it is considered non-fraud with a confidence level of 0.0.
This code serves as a basic example of fraud detection and can be customized or extended with more
advanced techniques as needed.

The code can be used as follows:

stream.map(FraudDetection())

'''

from pyflink.datastream.functions import MapFunction

class FraudDetection(MapFunction):
    def map(self, value):
        '''
        This method is called for each element in the input data stream. It applies the fraud
        detection logic to the element and returns the updated element with fraud-related
        information.

        :param value: The input data element
        :return: The updataed dat element with fraud-related information
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

