
class FraudDetection:
    @staticmethod
    def compute_fraud(record):
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

    @staticmethod
    def update_record(record):
        is_fraud, fraud_conf = FraudDetection.compute_fraud(record)
        record["is_fraud"] = is_fraud
        record["fraud_confidence"] = fraud_conf
        return record
