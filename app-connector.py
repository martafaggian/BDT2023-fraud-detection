from uuid import uuid4

from dash import Dash, dcc, html, Input, Output
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

app = Dash(__name__)
auth = PlainTextAuthProvider(username='bdtsu', password='25uWuYNi2b7JUgy4')
cluster = Cluster(['davidecalza.com'], port = 20042, auth_provider=auth)
session = cluster.connect()

session.set_keyspace('fraud_detection')
rows = session.execute("SELECT * FROM transactions LIMIT 5")

print([row for row in rows])
session.shutdown()
cluster.shutdown()


#if __name__ == '__main__':
    #app.run_server(debug=True)


