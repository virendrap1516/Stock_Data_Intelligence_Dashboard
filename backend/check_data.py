import sqlite3

def check_stock_data():
    conn = sqlite3.connect('data/stocks.db')
    cursor = conn.cursor()

    # Get RELIANCE.NS data
    cursor.execute('SELECT date, close FROM stock_data WHERE symbol = ? ORDER BY date DESC LIMIT 5', ('RELIANCE.NS',))
    print('RELIANCE.NS data:')
    for row in cursor.fetchall():
        print(row)

    # Get TCS.NS data
    cursor.execute('SELECT date, close FROM stock_data WHERE symbol = ? ORDER BY date DESC LIMIT 5', ('TCS.NS',))
    print('\nTCS.NS data:')
    for row in cursor.fetchall():
        print(row)

    # Check data types
    cursor.execute('SELECT * FROM stock_data LIMIT 1')
    columns = [description[0] for description in cursor.description]
    print('\nColumns in stock_data:')
    print(columns)

    conn.close()

if __name__ == "__main__":
    check_stock_data()