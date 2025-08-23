"""
Updated Library Management System with Annual Membership Fee Feature
"""

import json
import os
from datetime import datetime, timedelta
import uuid

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

class Member:
    """Updated Member class with annual membership fee"""
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
        member.membership_expiry_date = datetime.fromisoformat(data.get('membership_expiry_date', datetime.now().isoformat()))
        member.last_fee_payment_date = datetime.fromisoformat(data.get('last_fee_payment_date', datetime.now().isoformat()))
        return member

class LibraryManagementSystem:
    """Updated library system with membership fee support"""
    
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
                    data = json.load(f)
                
                self.books = {k: Book.from_dict(v) for k, v in data['books'].items()}
                self.members = {k: Member.from_dict(v) for k, v in data['members'].items()}
                self.transactions = {k: Transaction.from_dict(v) for k, v in data['transactions'].items()}
            except Exception as e:
                print(f"Error loading data: {e}")
    
    def update_member_fee(self, member_id, new_fee):
        """Update annual membership fee for a member"""
        if member_id in self.members:
            self.members[member_id].annual_membership_fee = new_fee
            self.save_data()
            return True
        return False
    
    def check_membership_status(self, member_id):
        """Check if membership is active and up-to-date"""
        if member_id in self.members:
            member = self.members[member_id]
            if datetime.now() > member.membership_expiry_date:
                return False, "Membership expired"
            return True, "Active"
        return False, "Member not found"
    
    def pay_membership_fee(self, member_id):
        """Process membership fee payment"""
        if member_id in self.members:
            member = self.members[member_id]
            member.membership_expiry_date = datetime.now() + timedelta(days=365)
            member.last_fee_payment_date = datetime.now()
            self.save_data()
            return True
        return False
    
    def get_members_with_fee_status(self):
        """Get all members with their fee status"""
        result = []
        for member_id, member in self.members.items():
            status, message = self.check_membership_status(member_id)
            result.append({
                'member_id': member_id,
                'name': member.name,
                'annual_fee': member.annual_membership_fee,
                'expiry_date': member.membership_expiry_date.isoformat(),
                'status': status,
                'status_message': message
            })
        return result
