from flask import Flask, render_template, request, redirect, url_for, session 
import mysql.connector 
import boto3 
from datetime import datetime, timedelta 
 
app = Flask(__name__) 
app.secret_key = 'SKaviyask@25' 
 
# Define stock level thresholds 
UNDERSTOCK_THRESHOLD = 10 
OVERSTOCK_THRESHOLD = 100 
EXPIRY_ALERT_DAYS = 7 
 
# AWS Configuration for SNS 
AWS_REGION = "ap-southeast-1" 
SNS_TOPIC_ARN = "arn:aws:sns:ap-southeast-1:051826731666:kaviya" 
     
# Database Configuration (AWS RDS) 
DB_HOST = "database-2.cdmqo2swyhou.ap-southeast-1.rds.amazonaws.com" 
DB_USER = "admin" 
DB_PASSWORD = "SKaviyask25" 
DB_NAME = "kaviya" 
 
 
# Connect to MySQL 
def get_db_connection(): 
    try: 
        conn = mysql.connector.connect( 
            host=DB_HOST, 
            user=DB_USER, 
            password=DB_PASSWORD, 
            database=DB_NAME 
        ) 
        return conn 
    except mysql.connector.Error as err: 
        print(f"Database connection error: {err}") 
        return None 
 
# Check stock levels 
def check_inventory(): 
    conn = get_db_connection()
    if conn is None: 
        return [], [] 
 
    cursor = conn.cursor(dictionary=True) 
    query = "SELECT Product, Category, Price, Quantity, Totalstock, Expirydate FROM Products" 
    cursor.execute(query) 
    products = cursor.fetchall() 
    cursor.close() 
    conn.close() 
 
    stock_issues = [] 
    expiry_issues = [] 
    today = datetime.now().date() 
    alert_date = today + timedelta(days=EXPIRY_ALERT_DAYS) 
 
    for product in products: 
        if product["Totalstock"] < UNDERSTOCK_THRESHOLD or product["Totalstock"] > OVERSTOCK_THRESHOLD: 
            stock_issues.append(product) 
        if product["Expirydate"] and product["Expirydate"] <= alert_date: 
            expiry_issues.append(product) 
 
    return stock_issues, expiry_issues 
 
# Send SMS Notification using AWS SNS 
def send_sms(message): 
    try: 
        sns_client = boto3.client("sns", region_name=AWS_REGION) 
        response = sns_client.publish( 
            TopicArn=SNS_TOPIC_ARN, 
Message=message 
        ) 
        print("Notification sent:", response) 
    except Exception as e: 
        print("Failed to send notification:", e) 
 
# Notify stock issues and expiry alerts 
def notify_issues(): 
    stock_issues, expiry_issues = check_inventory() 
    for product in stock_issues: 
        message = f"Stock Alert: {product['Product']} has {product['Totalstock']} units." 
        if product["Totalstock"] < UNDERSTOCK_THRESHOLD: 
            message += " It is UNDERSTOCKED." 
        elif product["Totalstock"] > OVERSTOCK_THRESHOLD: 
            message += " It is OVERSTOCKED." 
        send_sms(message)
        for product in expiry_issues: 
            message = f"Expiry Alert: {product['Product']} will expire on {product['Expirydate']}." 
        send_sms(message) 
 
@app.route('/') 
def login(): 
       return render_template('login.html') 
 
@app.route('/login', methods=['POST']) 
def do_login(): 
    username = request.form['username'] 
    password = request.form['password'] 
    if username == 'kaviya' and password == 'SKaviya@25': 
        session['logged_in'] = True 
        return redirect(url_for('dashboard')) 
    else: 
        return "Invalid Credentials" 
 
@app.route('/dashboard') 
def dashboard(): 
    if not session.get('logged_in'): 
        return redirect(url_for('login')) 
 
    conn = get_db_connection() 
    if conn is None: 
        return "Database connection error. Please try again later." 
 
    cursor = conn.cursor(dictionary=True) 
    cursor.execute("SELECT COUNT(*) AS Product_id FROM Products ") 
    Product_id = cursor.fetchone()["Product_id"] 
 
    # Fetch low stock products (Threshold: 10) 
    cursor.execute("SELECT COUNT(*) AS low_stock_count FROM Products WHERE totalstock < 10") 
    low_stock_count = cursor.fetchone()["low_stock_count"] 
 
    # Fetch reorder pending items 
    cursor.execute("SELECT COUNT(*) AS reorder_pending FROM reorders WHERE status = 'Pending'") 
    reorder_pending = cursor.fetchone()["reorder_pending"] 
 
    return render_template('dashboard.html', Product_id=Product_id, low_stock_count = low_stock_count,  reorder_pending=reorder_pending) 
 
@app.route('/example') 
def products(): 
    if not session.get('logged_in'):
          return redirect(url_for('login')) 
 
    conn = get_db_connection() 
    if conn is None: 
        return "Database connection error. Please try again later." 
 
    cursor = conn.cursor(dictionary=True) 
    cursor.execute("SELECT Product, Category, Price, Quantity, Totalstock, Expirydate FROM Products") 
    products = cursor.fetchall() 
    cursor.close() 
    conn.close() 
 
    return render_template('example.html', Products=products, 
                          understock_threshold=UNDERSTOCK_THRESHOLD, 
                           overstock_threshold=OVERSTOCK_THRESHOLD ) 
 
@app.route('/reorders') 
def reorders(): 
    if not session.get('logged_in'): 
        return redirect(url_for('login')) 
 
    conn = get_db_connection() 
    if conn is None: 
        return "Database connection error. Please try again later." 
 
    cursor = conn.cursor(dictionary=True) 
    cursor.execute(""" 
        SELECT r.reorder_id, p.Product, p.totalstock, r.status, s.email 
        FROM reorders r 
        JOIN Products p ON r.product_id = p.Product_id 
        JOIN suppliers s ON s.supplier_id = s.supplier_id 
        WHERE p.totalstock < 10 AND r.status = 'pending' 
    """) 
    reorders = cursor.fetchall() 
    cursor.close() 
    conn.close() 
 
    return render_template('reorders.html', reorders=reorders) 
 
@app.route('/approve_reorder/<int:reorder_id>', methods=['POST']) 
def approve_reorder(reorder_id): 
    conn = get_db_connection() 
    cursor = conn.cursor(dictionary=True) 
 
    cursor.execute("SELECT p.name, r.quantity, s.email FROM reorders r JOIN products p ON r.product_id = p.product_id JOIN suppliers s ON s.Supplier_id WHERE r.reorder_id = %s",(reorder_id,)) 
    reorder = cursor.fetchone() 
 
    if reorder: 
        cursor.execute("UPDATE reorders SET status = 'Approved' WHERE reorder_id = %s", 
(reorder_id,)) 
        conn.commit() 
 
        subject = "Reorder Approved" 
        message = f"Order approved for {reorder['quantity']} units of {reorder['name']}" 
        send_sns_email(subject, message) 
 
    cursor.close() 
    conn.close() 
    return redirect(url_for('reorders')) 
 
@app.route('/reject_reorder/<int:reorder_id>', methods=['POST']) 
def reject_reorder(reorder_id): 
    conn = get_db_connection() 
    cursor = conn.cursor() 
    cursor.execute("UPDATE reorders SET status = 'Rejected' WHERE reorder_id = %s", 
(reorder_id,)) 
    conn.commit() 
    cursor.close() 
    conn.close() 
    return redirect(url_for('reorders')) 
 
@app.route('/logout') 
def logout(): 
    session['logged_in'] = False 
    return redirect(url_for('login')) 
 
@app.route('/reports') 
def reports(): 
    if not session.get('logged_in'): 
        return redirect(url_for('login')) 
    conn = get_db_connection() 
    if conn is None: 
        return "Database connection error. Please try again later." 
 
    cursor = conn.cursor(dictionary=True) 
    cursor.execute("SELECT COUNT(*) AS low_stock_count FROM Products WHERE totalstock < 10") 
    low_stock_count = cursor.fetchone()["low_stock_count"] 
 
    cursor.execute("SELECT COUNT(*) AS expiring_soon FROM Products WHERE ExpiryDate <= '7'") 
    expiring_soon = cursor.fetchone()["expiring_soon"] 
 
    return render_template ('reports.html', low_stock_count = low_stock_count, expiring_soon = 
expiring_soon) 
 
if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000, debug=True)