echo 'LOADING SCHEMA...'
cqlsh cassandra-1 -f /schema.cql
cd /sources
echo 'LOADING ACCOUNTS...'
cqlsh cassandra-1 -e "COPY fraud_detection.accounts (balance, type, account_id, user_id, bank_id) FROM 'accounts.csv' WITH HEADER = TRUE"
echo 'LOADING BANKS...'
cqlsh cassandra-1 -e "COPY fraud_detection.banks (address, name, phone, bank_id) FROM 'banks.csv' WITH HEADER = TRUE"
echo 'LOADING USERS...'
cqlsh cassandra-1 -e "COPY fraud_detection.users (birthdate, email, name, registration_date, ssn, user_id) FROM 'users.csv' WITH HEADER = TRUE"
