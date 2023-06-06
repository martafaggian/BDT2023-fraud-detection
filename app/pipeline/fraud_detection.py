from pyflink.datastream.functions import MapFunction

class FraudDetection(MapFunction):
    def map(self, value):
        is_fraud, fraud_conf = self.compute_fraud(value)
        value["is_fraud"] = is_fraud
        value["fraud_confidence"] = fraud_conf
        return value

    def compute_fraud(self, record):
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

