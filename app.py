
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime, timedelta
import uuid
import logging

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

class Book:
    """Represents a book in the library"""
    def __init__(self, book_id, title, author, isbn, genre, total_copies):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.genre = genre
        self.total_copies = total_copies
        self.available_copies = total_copies
        self.is_available = True
    
    def to_dict(self):
        return {
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'genre': self.genre,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'is_available': self.is_available
        }
    
    @classmethod
    def from_dict(cls, data):
        book = cls(
            data['book_id'], data['title'], data['author'],
            data['isbn'], data['genre'], data['total_copies']
        )
        book.available_copies = data['available_copies']
        book.is_available = data['is_available']
        return book

class Member:
    """Represents a library member with annual membership fee"""
    def __init__(self, member_id, name, email, phone):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.phone = phone
        self.borrowed_books = []
        self.membership_date = datetime.now()
        self.is_active = True
        self.annual_membership_fee = 50.0  # Default annual fee
        self.membership_expiry_date = datetime.now() + timedelta(days=365)
        self.last_fee_payment_date = datetime.now()
    
    def to_dict(self):
        return {
            'member_id': self.member_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'borrowed_books': self.borrowed_books,
            'membership_date': self.membership_date.isoformat(),
            'is_active': self.is_active,
            'annual_membership_fee': self.annual_membership_fee,
            'membership_expiry_date': self.membership_expiry_date.isoformat(),
            'last_fee_payment_date': self.last_fee_payment_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        member = cls(
            data['member_id'], data['name'], data['email'], data['phone']
        )
        member.borrowed_books = data['borrowed_books']
        member.membership_date = datetime.fromisoformat(data['membership_date'])
        member.is_active = data['is_active']
        member.annual_membership_fee = data.get('annual_membership_fee', 50.0)
        
        if 'membership_expiry_date' in data:
            member.membership_expiry_date = datetime.fromisoformat(data['membership_expiry_date'])
        else:
            member.membership_expiry_date = datetime.now() + timedelta(days=365)  # Default to one year from now
        
        if 'last_fee_payment_date' in data:
            member.last_fee_payment_date = datetime.fromisoformat(data['last_fee_payment_date'])
        else:
            member.last_fee_payment_date = datetime.now()  # Default to current time
        return member

class Transaction:
    """Represents a borrowing transaction"""
    def __init__(self, transaction_id, member_id, book_id, borrow_date, due_date):
        self.transaction_id = transaction_id
        self.member_id = member_id
        self.book_id = book_id
        self.borrow_date = borrow_date
        self.due_date = due_date
        self.return_date = None
        self.fine = 0.0
    
    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'member_id': self.member_id,
            'book_id': self.book_id,
            'borrow_date': self.borrow_date.isoformat(),
            'due_date': self.due_date.isoformat(),
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'fine': self.fine
        }
    
    @classmethod
    def from_dict(cls, data):
        transaction = cls(
            data['transaction_id'], data['member_id'], data['book_id'],
            datetime.fromisoformat(data['borrow_date']),
            datetime.fromisoformat(data['due_date'])
        )
        if data['return_date']:
            transaction.return_date = datetime.fromisoformat(data['return_date'])
        transaction.fine = data['fine']
        return transaction

class LibraryManagementSystem:
    """Main library management system class"""
    
    def __init__(self):
        self.books = {}
        self.members = {}
        self.transactions = {}
        self.data_file = 'library_data_updated.json'
        self.load_data()
    
    def save_data(self):
        """Save all data to JSON file"""
        data = {
            'books': {k: v.to_dict() for k, v in self.books.items()},
            'members': {k: v.to_dict() for k, v in self.members.items()},
            'transactions': {k: v.to_dict() for k, v in self.transactions.items()}
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        """Load data from JSON file if it exists"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    logging.info("Loading data from JSON file.")
                    data = json.load(f)
                
                self.books = {k: Book.from_dict(v) for k, v in data['books'].items()}
                self.members = {k: Member.from_dict(v) for k, v in data['members'].items()}
                self.transactions = {k: Transaction.from_dict(v) for k, v in data['transactions'].items()}
            except Exception as e:
                logging.error(f"Error loading data: {e}")

library = LibraryManagementSystem()

@app.route('/')
def index():
    stats = {
        'total_books': len(library.books),
        'total_members': len(library.members),
        'total_transactions': len(library.transactions),
        'available_books': sum(book.available_copies for book in library.books.values()),
        'borrowed_books': sum(1 for t in library.transactions.values() if t.return_date is None)
    }
    return render_template('index.html', stats=stats)

@app.route('/books')
def books():
    return render_template('books.html', books=library.books.values())

@app.route('/members')
def members():
    return render_template('members.html', members=library.members.values())

@app.route('/transactions')
def transactions():
    logging.info(f"Transactions loaded: {len(library.transactions)}")
    for transaction in library.transactions.values():
        logging.info(f"Transaction ID: {transaction.transaction_id}, Member ID: {transaction.member_id}, Book ID: {transaction.book_id}")
    return render_template('transactions.html', transactions=library.transactions.values())

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        book_id = str(uuid.uuid4())[:8]
        book = Book(
            book_id,
            request.form['title'],
            request.form['author'],
            request.form['isbn'],
            request.form['genre'],
            int(request.form['total_copies'])
        )
        library.books[book_id] = book  # Add new book
        library.save_data()
        return redirect(url_for('books'))
    return render_template('add_book.html')

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        member_id = str(uuid.uuid4())[:8]
        member = Member(
            member_id,
            request.form['name'],
            request.form['email'],
            request.form['phone']
        )
        library.members[member_id] = member
        library.save_data()
        return redirect(url_for('members'))
    return render_template('add_member.html')

@app.route('/borrow_book', methods=['GET', 'POST'])
def borrow_book():
    if request.method == 'POST':
        member_id = request.form['member_id']
        book_id = request.form['book_id']
        
        if member_id not in library.members or book_id not in library.books:
            return jsonify({'error': 'Invalid member or book ID'})
        
        member = library.members[member_id]
        book = library.books[book_id]
        
        if not member.is_active:
            return jsonify({'error': 'Member account is inactive'})
        
        if book.available_copies <= 0:
            return jsonify({'error': 'Book not available'})
        
        if len(member.borrowed_books) >= 3:
            return jsonify({'error': 'Member has reached maximum borrowing limit'})
        
        transaction_id = str(uuid.uuid4())[:8]
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=14)
        
        transaction = Transaction(transaction_id, member_id, book_id, borrow_date, due_date)
        library.transactions[transaction_id] = transaction
        
        book.available_copies -= 1
        if book.available_copies == 0:
            book.is_available = False
        
        member.borrowed_books.append(transaction_id)
        library.save_data()
        
        return redirect(url_for('transactions'))
    
    return render_template('borrow_book.html', 
                         books=library.books.values(), 
                         members=library.members.values())

@app.route('/return_book/<transaction_id>')
def return_book(transaction_id):
    if transaction_id not in library.transactions:
        return jsonify({'error': 'Invalid transaction ID'})
    
    transaction = library.transactions[transaction_id]
    
    if transaction.return_date is not None:
        return jsonify({'error': 'Book already returned'})
    
    transaction.return_date = datetime.now()
    
    if transaction.return_date > transaction.due_date:
        overdue_days = (transaction.return_date - transaction.due_date).days
        transaction.fine = overdue_days * 1.0
    
    book = library.books[transaction.book_id]
    book.available_copies += 1
    book.is_available = True
    
    member = library.members[transaction.member_id]
    member.borrowed_books.remove(transaction_id)
    
    library.save_data()
    return redirect(url_for('transactions'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    search_by = request.args.get('by', 'title')
    
    if query:
        results = []
        query = query.lower()
        
        for book in library.books.values():
            if search_by == 'title' and query in book.title.lower():
                results.append(book)
            elif search_by == 'author' and query in book.author.lower():
                results.append(book)
            elif search_by == 'isbn' and query in book.isbn.lower():
                results.append(book)
            elif search_by == 'genre' and query in book.genre.lower():
                results.append(book)
        
        return render_template('search.html', books=results, query=query)
    
    return render_template('search.html', books=[], query='')

@app.errorhandler(404)
def page_not_found(e):
    logging.error('404 error: Page not found.')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    logging.error('500 error: Internal server error.')
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
