# database/init_db.py
import sqlite3
import os

DB_PATH = 'database/erp.db'

def create_database():
    """Initialize the ERP database with sample tables and data."""
    
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute('''
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create leads table
    cursor.execute('''
        CREATE TABLE leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT,
            status TEXT DEFAULT 'new',
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price DECIMAL(10,2),
            stock_quantity INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount DECIMAL(10,2),
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    # Create order_items table
    cursor.execute('''
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price DECIMAL(10,2),
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Create invoices table
    cursor.execute('''
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            order_id INTEGER,
            invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            amount DECIMAL(10,2),
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
    ''')
    
    # Create payments table
    cursor.execute('''
        CREATE TABLE payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            amount DECIMAL(10,2),
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            method TEXT,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        )
    ''')
    
    # Insert sample data
    sample_customers = [
        ('John Doe', 'john@example.com', '555-0101', '123 Main St, City, State'),
        ('Jane Smith', 'jane@example.com', '555-0102', '456 Oak Ave, City, State'),
        ('Bob Johnson', 'bob@example.com', '555-0103', '789 Pine Rd, City, State')
    ]
    
    cursor.executemany('''
        INSERT INTO customers (name, email, phone, address)
        VALUES (?, ?, ?, ?)
    ''', sample_customers)
    
    sample_leads = [
        ('Alice Brown', 'alice@company.com', 'TechCorp', 'new', 'website'),
        ('Charlie Wilson', 'charlie@startup.io', 'StartupInc', 'qualified', 'referral'),
        ('Diana Prince', 'diana@enterprise.net', 'Enterprise Corp', 'contacted', 'social')
    ]
    
    cursor.executemany('''
        INSERT INTO leads (name, email, company, status, source)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_leads)
    
    sample_products = [
        ('P-001', 'Laptop Pro', 'High-performance laptop', 1299.99, 50),
        ('P-002', 'Wireless Mouse', 'Ergonomic wireless mouse', 29.99, 200),
        ('P-003', 'USB Cable', 'USB-C charging cable', 19.99, 150),
        ('P-004', 'Monitor 24"', '24-inch LED monitor', 299.99, 75),
        ('P-005', 'Keyboard', 'Mechanical keyboard', 89.99, 100)
    ]
    
    cursor.executemany('''
        INSERT INTO products (sku, name, description, price, stock_quantity)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_products)
    
    # Create some sample orders
    cursor.execute('''
        INSERT INTO orders (customer_id, total_amount, status)
        VALUES (1, 1329.98, 'completed')
    ''')
    
    cursor.execute('''
        INSERT INTO orders (customer_id, total_amount, status)
        VALUES (2, 389.98, 'pending')
    ''')
    
    # Create order items
    cursor.execute('''
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        VALUES (1, 1, 1, 1299.99)
    ''')
    
    cursor.execute('''
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        VALUES (1, 2, 1, 29.99)
    ''')
    
    cursor.execute('''
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        VALUES (2, 4, 1, 299.99)
    ''')
    
    cursor.execute('''
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        VALUES (2, 5, 1, 89.99)
    ''')
    
    # Create sample invoices
    cursor.execute('''
        INSERT INTO invoices (customer_id, order_id, amount, status)
        VALUES (1, 1, 1329.98, 'paid')
    ''')
    
    cursor.execute('''
        INSERT INTO invoices (customer_id, order_id, amount, status)
        VALUES (2, 2, 389.98, 'pending')
    ''')
    
    # Create sample payment
    cursor.execute('''
        INSERT INTO payments (invoice_id, amount, method)
        VALUES (1, 1329.98, 'credit_card')
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized successfully at {DB_PATH}")
    print("Sample data inserted for testing.")

if __name__ == "__main__":
    create_database()
