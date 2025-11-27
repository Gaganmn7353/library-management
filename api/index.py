from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import csv
import io
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Use in-memory storage for Vercel (or integrate with external DB)
# For production, use MongoDB, PostgreSQL, or Firebase
DATA_FILE = '/tmp/library_data.json'

def load_data():
    """Load data from file or return default structure"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'books': [],
        'users': [],
        'transactions': [],
        'counters': {'book_id': 1, 'user_id': 1, 'transaction_id': 1}
    }

def save_data(data):
    """Save data to file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Root route
@app.route('/')
def home():
    return jsonify({'message': 'Library Management API', 'status': 'running'})

# BOOKS API
@app.route('/api/books', methods=['GET'])
def get_books():
    data = load_data()
    return jsonify(data['books'])

@app.route('/api/books', methods=['POST'])
def add_book():
    data = load_data()
    book_data = request.json
    
    new_book = {
        'id': data['counters']['book_id'],
        'title': book_data['title'],
        'author': book_data['author'],
        'isbn': book_data.get('isbn', ''),
        'quantity': book_data['quantity'],
        'available': book_data['quantity'],
        'created_at': datetime.now().isoformat()
    }
    
    data['books'].append(new_book)
    data['counters']['book_id'] += 1
    save_data(data)
    
    return jsonify({'id': new_book['id'], 'message': 'Book added successfully'}), 201

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    data = load_data()
    data['books'] = [b for b in data['books'] if b['id'] != book_id]
    save_data(data)
    return jsonify({'message': 'Book deleted successfully'})

# USERS API
@app.route('/api/users', methods=['GET'])
def get_users():
    data = load_data()
    return jsonify(data['users'])

@app.route('/api/users', methods=['POST'])
def add_user():
    data = load_data()
    user_data = request.json
    
    # Check for duplicate email
    if any(u['email'] == user_data['email'] for u in data['users']):
        return jsonify({'error': 'Email already exists'}), 400
    
    new_user = {
        'id': data['counters']['user_id'],
        'name': user_data['name'],
        'email': user_data['email'],
        'phone': user_data.get('phone', ''),
        'books_issued': 0,
        'created_at': datetime.now().isoformat()
    }
    
    data['users'].append(new_user)
    data['counters']['user_id'] += 1
    save_data(data)
    
    return jsonify({'id': new_user['id'], 'message': 'User added successfully'}), 201

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    data = load_data()
    data['users'] = [u for u in data['users'] if u['id'] != user_id]
    save_data(data)
    return jsonify({'message': 'User deleted successfully'})

# TRANSACTIONS API
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    data = load_data()
    return jsonify(data['transactions'])

@app.route('/api/transactions/issue', methods=['POST'])
def issue_book():
    data = load_data()
    trans_data = request.json
    
    # Find book
    book = next((b for b in data['books'] if b['id'] == trans_data['book_id']), None)
    if not book or book['available'] <= 0:
        return jsonify({'error': 'Book not available'}), 400
    
    # Find user
    user = next((u for u in data['users'] if u['id'] == trans_data['user_id']), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Create transaction
    new_transaction = {
        'id': data['counters']['transaction_id'],
        'book_id': book['id'],
        'book_title': book['title'],
        'user_id': user['id'],
        'user_name': user['name'],
        'issue_date': datetime.now().isoformat(),
        'return_date': None,
        'status': 'issued'
    }
    
    # Update book availability
    book['available'] -= 1
    
    # Update user books issued
    user['books_issued'] += 1
    
    data['transactions'].append(new_transaction)
    data['counters']['transaction_id'] += 1
    save_data(data)
    
    return jsonify({'id': new_transaction['id'], 'message': 'Book issued successfully'}), 201

@app.route('/api/transactions/return/<int:transaction_id>', methods=['PUT'])
def return_book(transaction_id):
    data = load_data()
    
    # Find transaction
    transaction = next((t for t in data['transactions'] if t['id'] == transaction_id), None)
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    # Update transaction
    transaction['return_date'] = datetime.now().isoformat()
    transaction['status'] = 'returned'
    
    # Update book availability
    book = next((b for b in data['books'] if b['id'] == transaction['book_id']), None)
    if book:
        book['available'] += 1
    
    # Update user books issued
    user = next((u for u in data['users'] if u['id'] == transaction['user_id']), None)
    if user:
        user['books_issued'] -= 1
    
    save_data(data)
    
    return jsonify({'message': 'Book returned successfully'})

# EXPORT API
@app.route('/api/export/books', methods=['GET'])
def export_books():
    data = load_data()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Title', 'Author', 'ISBN', 'Quantity', 'Available', 'Created At'])
    
    for book in data['books']:
        writer.writerow([
            book['id'], book['title'], book['author'], book['isbn'],
            book['quantity'], book['available'], book['created_at']
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='books.csv'
    )

@app.route('/api/export/users', methods=['GET'])
def export_users():
    data = load_data()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Books Issued', 'Created At'])
    
    for user in data['users']:
        writer.writerow([
            user['id'], user['name'], user['email'], user['phone'],
            user['books_issued'], user['created_at']
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='users.csv'
    )

@app.route('/api/export/transactions', methods=['GET'])
def export_transactions():
    data = load_data()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Book Title', 'User Name', 'Issue Date', 'Return Date', 'Status'])
    
    for trans in data['transactions']:
        writer.writerow([
            trans['id'], trans['book_title'], trans['user_name'],
            trans['issue_date'], trans['return_date'] or 'N/A', trans['status']
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='transactions.csv'
    )

# Vercel serverless handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()

# For local testing
if __name__ == '__main__':
    app.run(debug=True)