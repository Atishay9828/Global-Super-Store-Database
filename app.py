from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='superstore'
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/customers')
def customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM customers')
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view.html', data=customers, title="Customers")

@app.route('/edit/customers/<id>', methods=['GET', 'POST'])
def edit_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM customers WHERE CustomerID = %s', (id,))
    row = cursor.fetchone()

    if request.method == 'POST':
        fullName = request.form['FullName']
        segment = request.form['Segment']
        cursor.execute('UPDATE customers SET FullName=%s, Segment=%s WHERE CustomerID=%s',
                       (fullName, segment, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/customers')
    
    cursor.close()
    conn.close()
    return render_template('edit.html', row=row, table='customers')

@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('inventory.html', data=data)


@app.route('/sales_lookup', methods=['GET', 'POST'])
def sales_lookup():
    sales_data = []
    search_term = ""
    searched = False

    if request.method == 'POST':
        search_term = request.form['search']
        searched = True
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = '''
        SELECT 
            p.ProductID,
            p.ProductName,
            SUM(o.Quantity) as TotalQuantity,
            SUM(s.sales) as TotalSales
        FROM products p
        JOIN orders o ON p.ProductID = o.ProductID
        JOIN sales s ON o.OrderID = s.OrderID
        WHERE p.ProductID = %s OR p.ProductName LIKE %s
        GROUP BY p.ProductID, p.ProductName
        '''
        cursor.execute(query, (search_term, f'%{search_term}%'))
        sales_data = cursor.fetchall()

        cursor.close()
        conn.close()

    return render_template('sales_lookup.html', sales_data=sales_data, search_term=search_term, searched=searched)
@app.route('/shipping')
def view_shipping():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT s.OrderID, s.ShippingDate, s.ShippingMode, s.ShippingCost,
       a.City, a.State, a.Country, a.Region
FROM shipping s
JOIN address a ON s.AddressID = a.AddressID;

    """
    cursor.execute(query)
    shipping_data = cursor.fetchall()
    cursor.close()
    return render_template('shipping.html', data=shipping_data)
@app.route('/orders')
def view_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT o.OrderID, p.ProductName, c.FullName, o.Quantity, o.OrderDate, o.Market, o.OrderPriority
        FROM Orders o
        JOIN Products p ON o.ProductID = p.ProductID
        JOIN Customers c ON o.CustomerID = c.CustomerID
    """
    cursor.execute(query)
    order_data = cursor.fetchall()
    cursor.close()
    return render_template('orders.html', data=order_data)


if __name__ == '__main__':
    app.run(debug=True)