from flask import Flask, jsonify, request, render_template
import pandas as pd
import requests
import json

app = Flask(__name__)

@app.route('/')
def query_transactions():
    data = pd.read_csv("transactions.csv")
    result = []
    for index, row in data.iterrows():
        result.append({
                'user_id' : row['user_id'],
                'transaction_id': row['transaction_id'],
                'timestamp': row['timestamp'],
                'account_type': row['account_type'],
                'amount': row['amount'],
                'is_fraud': row['is_fraud'],
                'account_id': row['account_id']
        })
    if result:
        with open("result.json", "w") as file:
            json.dump(result, file)
        return result
    return jsonify({'fraud': 'data not found'})

@app.route('/user/<user_id>', methods = ['GET'])
def get_user_transactions(user_id):
    data = requests.get('http://127.0.0.1:9999/').json()
    transactions = [t for t in data if t['user_id'] == user_id]
    return jsonify(transactions)


if __name__ == '__main__':
    app.run(debug=True, port=9999)
