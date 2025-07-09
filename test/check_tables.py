import sqlite3

conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

# Check what tables exist
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [row[0] for row in cursor.fetchall()]
migration_tables = ['currencies', 'client_balances', 'client_commissions', 'currency_rates']

print('Migration tables status:')
for table in migration_tables:
    if table in tables:
        print(f'  {table}: EXISTS')
    else:
        print(f'  {table}: MISSING')

print('\nAll tables in database:')
for table in sorted(tables):
    print(f'  {table}')

conn.close()
