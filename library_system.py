"""
Library Management System
A professional Python-based solution for managing library operations
"""

import json
import os
from datetime import datetime, timedelta
from collections import deque
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for Windows
colorama.init()

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
    """Represents a library member"""
    def __init__(self, member_id, name, email, phone):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.phone = phone
        self.borrowed_books = []
        self.membership_date = datetime.now()
        self.is_active = True
    
    def to_dict(self):
        return {
            'member_id': self.member_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'borrowed_books': self.borrowed_books,
            'membership_date': self.membership_date.isoformat(),
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data):
        member = cls(
            data['member_id'], data['name'], data['email'], data['phone']
        )
        member.borrowed_books = data['borrowed_books']
        member.membership_date = datetime.fromisoformat(data['membership_date'])
        member.is_active = data['is_active']
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
        self.books = {}  # book_id -> Book object
        self.members = {}  # member_id -> Member object
        self.transactions = {}  # transaction_id -> Transaction object
        self.book_queue = deque()  # Queue for book reservations
        self.transaction_stack = []  # Stack for recent transactions
        
        self.book_counter = 1000
        self.member_counter = 100
        self.transaction_counter = 10000
        
        self.data_file = 'library_data.json'
        self.load_data()
    
    def save_data(self):
        """Save all data to JSON file"""
        data = {
            'books': {k: v.to_dict() for k, v in self.books.items()},
            'members': {k: v.to_dict() for k, v in self.members.items()},
            'transactions': {k: v.to_dict() for k, v in self.transactions.items()},
            'book_counter': self.book_counter,
            'member_counter': self.member_counter,
            'transaction_counter': self.transaction_counter
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
                
                self.book_counter = data['book_counter']
                self.member_counter = data['member_counter']
                self.transaction_counter = data['transaction_counter']
                
                print(Fore.GREEN + "Data loaded successfully!" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"Error loading data: {e}" + Style.RESET_ALL)
    
    def add_book(self, title, author, isbn, genre, total_copies):
        """Add a new book to the library"""
        book_id = f"B{self.book_counter}"
        self.book_counter += 1
        
        book = Book(book_id, title, author, isbn, genre, total_copies)
        self.books[book_id] = book
        
        self.save_data()
        return book_id
    
    def update_book(self, book_id, **kwargs):
        """Update book information"""
        if book_id not in self.books:
            return False
        
        book = self.books[book_id]
        for key, value in kwargs.items():
            if hasattr(book, key):
                setattr(book, key, value)
        
        self.save_data()
        return True
    
    def delete_book(self, book_id):
        """Delete a book from the library"""
        if book_id not in self.books:
            return False
        
        # Check if book has active transactions
        active_transactions = [
            t for t in self.transactions.values() 
            if t.book_id == book_id and t.return_date is None
        ]
        
        if active_transactions:
            return False
        
        del self.books[book_id]
        self.save_data()
        return True
    
    def register_member(self, name, email, phone):
        """Register a new member"""
        member_id = f"M{self.member_counter}"
        self.member_counter += 1
        
        member = Member(member_id, name, email, phone)
        self.members[member_id] = member
        
        self.save_data()
        return member_id
    
    def update_member(self, member_id, **kwargs):
        """Update member information"""
        if member_id not in self.members:
            return False
        
        member = self.members[member_id]
        for key, value in kwargs.items():
            if hasattr(member, key):
                setattr(member, key, value)
        
        self.save_data()
        return True
    
    def borrow_book(self, member_id, book_id):
        """Process book borrowing"""
        if member_id not in self.members or book_id not in self.books:
            return False, "Invalid member or book ID"
        
        member = self.members[member_id]
        book = self.books[book_id]
        
        if not member.is_active:
            return False, "Member account is inactive"
        
        if book.available_copies <= 0:
            return False, "Book not available"
        
        if len(member.borrowed_books) >= 3:
            return False, "Member has reached maximum borrowing limit (3 books)"
        
        transaction_id = f"T{self.transaction_counter}"
        self.transaction_counter += 1
        
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=14)
        
        transaction = Transaction(transaction_id, member_id, book_id, borrow_date, due_date)
        self.transactions[transaction_id] = transaction
        
        book.available_copies -= 1
        if book.available_copies == 0:
            book.is_available = False
        
        member.borrowed_books.append(transaction_id)
        
        # Add to transaction stack
        self.transaction_stack.append(transaction)
        
        self.save_data()
        return True, transaction_id
    
    def return_book(self, transaction_id):
        """Process book return"""
        if transaction_id not in self.transactions:
            return False, "Invalid transaction ID"
        
        transaction = self.transactions[transaction_id]
        
        if transaction.return_date is not None:
            return False, "Book already returned"
        
        transaction.return_date = datetime.now()
        
        # Calculate fine if overdue
        if transaction.return_date > transaction.due_date:
            overdue_days = (transaction.return_date - transaction.due_date).days
            transaction.fine = overdue_days * 1.0  # $1 per day
        
        book = self.books[transaction.book_id]
        book.available_copies += 1
        book.is_available = True
        
        member = self.members[transaction.member_id]
        member.borrowed_books.remove(transaction_id)
        
        self.save_data()
        return True, transaction.fine
    
    def search_books(self, query, search_by='title'):
        """Search books by title, author, ISBN, or genre"""
        results = []
        query = query.lower()
        
        for book in self.books.values():
            if search_by == 'title' and query in book.title.lower():
                results.append(book)
            elif search_by == 'author' and query in book.author.lower():
                results.append(book)
            elif search_by == 'isbn' and query in book.isbn.lower():
                results.append(book)
            elif search_by == 'genre' and query in book.genre.lower():
                results.append(book)
        
        return results
    
    def get_member_history(self, member_id):
        """Get borrowing history for a member"""
        if member_id not in self.members:
            return []
        
        member_transactions = [
            t for t in self.transactions.values()
            if t.member_id == member_id
        ]
        
        return sorted(member_transactions, key=lambda x: x.borrow_date, reverse=True)
    
    def get_statistics(self):
        """Get library statistics"""
        total_books = len(self.books)
        total_members = len(self.members)
        total_transactions = len(self.transactions)
        
        borrowed_books = sum(
            1 for t in self.transactions.values()
            if t.return_date is None
        )
        
        available_books = sum(
            book.available_copies for book in self.books.values()
        )
        
        overdue_transactions = [
            t for t in self.transactions.values()
            if t.return_date is None and datetime.now() > t.due_date
        ]
        
        top_borrowers = {}
        for transaction in self.transactions.values():
            if transaction.member_id not in top_borrowers:
                top_borrowers[transaction.member_id] = 0
            top_borrowers[transaction.member_id] += 1
        
        top_borrowers = sorted(
            top_borrowers.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_books': total_books,
            'total_members': total_members,
            'total_transactions': total_transactions,
            'borrowed_books': borrowed_books,
            'available_books': available_books,
            'overdue_transactions': len(overdue_transactions),
            'total_fines': sum(t.fine for t in self.transactions.values()),
            'top_borrowers': top_borrowers
        }

class LibraryInterface:
    """Console interface for the library management system"""
    
    def __init__(self):
        self.library = LibraryManagementSystem()
    
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Print formatted header"""
        print(Fore.CYAN + "=" * 60)
        print(f"{title:^60}")
        print("=" * 60 + Style.RESET_ALL)
    
    def print_menu(self, options, title="Menu"):
        """Display menu options"""
        self.print_header(title)
        for i, (key, description) in enumerate(options.items(), 1):
            print(f"{Fore.YELLOW}{i}. {description}{Style.RESET_ALL}")
        print(Fore.CYAN + "-" * 60 + Style.RESET_ALL)
    
    def get_input(self, prompt, input_type=str):
        """Get validated user input"""
        while True:
            try:
                user_input = input(Fore.GREEN + prompt + Style.RESET_ALL)
                if input_type == int:
                    return int(user_input)
                elif input_type == float:
                    return float(user_input)
                return user_input.strip()
            except ValueError:
                print(Fore.RED + "Invalid input. Please try again." + Style.RESET_ALL)
    
    def display_book(self, book):
        """Display book details"""
        print(f"\n{Fore.CYAN}Book ID: {book.book_id}")
        print(f"Title: {book.title}")
        print(f"Author: {book.author}")
        print(f"ISBN: {book.isbn}")
        print(f"Genre: {book.genre}")
        print(f"Total Copies: {book.total_copies}")
        print(f"Available Copies: {book.available_copies}")
        print(f"Status: {'Available' if book.is_available else 'Not Available'}{Style.RESET_ALL}")
    
    def display_member(self, member):
        """Display member details"""
        print(f"\n{Fore.CYAN}Member ID: {member.member_id}")
        print(f"Name: {member.name}")
        print(f"Email: {member.email}")
        print(f"Phone: {member.phone}")
        print(f"Membership Date: {member.membership_date.strftime('%Y-%m-%d')}")
        print(f"Status: {'Active' if member.is_active else 'Inactive'}")
        print(f"Borrowed Books: {len(member.borrowed_books)}{Style.RESET_ALL}")
    
    def display_transaction(self, transaction):
        """Display transaction details"""
        book = self.library.books[transaction.book_id]
        member = self.library.members[transaction.member_id]
        
        print(f"\n{Fore.CYAN}Transaction ID: {transaction.transaction_id}")
        print(f"Member: {member.name} ({member.member_id})")
        print(f"Book: {book.title} ({book.book_id})")
        print(f"Borrow Date: {transaction.borrow_date.strftime('%Y-%m-%d')}")
        print(f"Due Date: {transaction.due_date.strftime('%Y-%m-%d')}")
        if transaction.return_date:
            print(f"Return Date: {transaction.return_date.strftime('%Y-%m-%d')}")
            print(f"Fine: ${transaction.fine:.2f}")
        else:
            print(f"Status: {Fore.RED}Not Returned{Style.RESET_ALL}")
        print("-" * 50 + Style.RESET_ALL)
    
    def display_statistics(self):
        """Display library statistics"""
        stats = self.library.get_statistics()
        
        self.print_header("Library Statistics")
        print(f"{Fore.GREEN}Total Books: {stats['total_books']}")
        print(f"Total Members: {stats['total_members']}")
        print(f"Total Transactions: {stats['total_transactions']}")
        print(f"Books Currently Borrowed: {stats['borrowed_books']}")
        print(f"Books Available: {stats['available_books']}")
        print(f"Overdue Transactions: {stats['overdue_transactions']}")
        print(f"Total Fines Collected: ${stats['total_fines']:.2f}{Style.RESET_ALL}")
        
        if stats['top_borrowers']:
            print(f"\n{Fore.YELLOW}Top 5 Borrowers:")
            for member_id, count in stats['top_borrowers']:
                member = self.library.members[member_id]
                print(f"  {member.name}: {count} books{Style.RESET_ALL}")
    
    def add_book_menu(self):
        """Menu for adding a new book"""
        self.print_header("Add New Book")
        
        title = self.get_input("Enter book title: ")
        author = self.get_input("Enter author name: ")
        isbn = self.get_input("Enter ISBN: ")
        genre = self.get_input("Enter genre: ")
        total_copies = self.get_input("Enter total copies: ", int)
        
        book_id = self.library.add_book(title, author, isbn, genre, total_copies)
        print(Fore.GREEN + f"\nBook added successfully! Book ID: {book_id}" + Style.RESET_ALL)
        input("\nPress Enter to continue...")
    
    def search_books_menu(self):
        """Menu for searching books"""
        self.print_header("Search Books")
        
        search_options = {
            'title': 'Search by Title',
            'author': 'Search by Author',
            'isbn': 'Search by ISBN',
            'genre': 'Search by Genre'
        }
        
        self.print_menu(search_options, "Search By")
        choice = self.get_input("Enter your choice: ", int)
        
        if 1 <= choice <= 4:
            search_by = list(search_options.keys())[choice - 1]
            query = self.get_input("Enter search query: ")
            
            results = self.library.search_books(query, search_by)
            
            if results:
                print(f"\n{Fore.GREEN}Found {len(results)} book(s):{Style.RESET_ALL}")
                for book in results:
                    self.display_book(book)
            else:
                print(Fore.RED + "No books found matching your query." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Invalid choice." + Style.RESET_ALL)
        
        input("\nPress Enter to continue...")
    
    def borrow_book_menu(self):
        """Menu for borrowing a book"""
        self.print_header("Borrow Book")
        
        member_id = self.get_input("Enter member ID: ")
        book_id = self.get_input("Enter book ID: ")
        
        success, message = self.library.borrow_book(member_id, book_id)
        
        if success:
            print(Fore.GREEN + f"\nBook borrowed successfully! Transaction ID: {message}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"\nError: {message}" + Style.RESET_ALL)
        
        input("\nPress Enter to continue...")
    
    def return_book_menu(self):
        """Menu for returning a book"""
        self.print_header("Return Book")
        
        transaction_id = self.get_input("Enter transaction ID: ")
        
        success, fine = self.library.return_book(transaction_id)
        
        if success:
            if fine > 0:
                print(Fore.YELLOW + f"\nBook returned successfully! Fine due: ${fine:.2f}" + Style.RESET_ALL)
            else:
                print(Fore.GREEN + "\nBook returned successfully! No fine due." + Style.RESET_ALL)
        else:
            print(Fore.RED + f"\nError: {fine}" + Style.RESET_ALL)
        
        input("\nPress Enter to continue...")
    
    def view_member_history_menu(self):
        """Menu for viewing member borrowing history"""
        self.print_header("Member Borrowing History")
        
        member_id = self.get_input("Enter member ID: ")
        
        if member_id not in self.library.members:
            print(Fore.RED + "Member not found." + Style.RESET_ALL)
        else:
            history = self.library.get_member_history(member_id)
            member = self.library.members[member_id]
            
            print(f"\n{Fore.CYAN}Borrowing history for {member.name}:{Style.RESET_ALL}")
            
            if history:
                for transaction in history:
                    self.display_transaction(transaction)
            else:
                print(Fore.YELLOW + "No borrowing history found." + Style.RESET_ALL)
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main application loop"""
        while True:
            self.clear_screen()
            
            main_menu = {
                '1': 'Book Management',
                '2': 'Member Management',
                '3': 'Borrow/Return Books',
                '4': 'Search Books',
                '5': 'View Statistics',
                '6': 'View Member History',
                '7': 'Exit'
            }
            
            self.print_menu(main_menu, "Library Management System")
            
            choice = self.get_input("Enter your choice: ", int)
            
            if choice == 1:
                # Book Management submenu
                book_menu = {
                    '1': 'Add New Book',
                    '2': 'Update Book',
                    '3': 'Delete Book',
                    '4': 'List All Books',
                    '5': 'Back to Main Menu'
                }
                
                while True:
                    self.clear_screen()
                    self.print_menu(book_menu, "Book Management")
                    
                    sub_choice = self.get_input("Enter your choice: ", int)
                    
                    if sub_choice == 1:
                        self.add_book_menu()
                    elif sub_choice == 2:
                        # Update book logic
                        pass
                    elif sub_choice == 3:
                        # Delete book logic
                        pass
                    elif sub_choice == 4:
                        # List books logic
                        pass
                    elif sub_choice == 5:
                        break
                    else:
                        print(Fore.RED + "Invalid choice. Please try again." + Style.RESET_ALL)
                        input("\nPress Enter to continue...")
            
            elif choice == 2:
                # Member Management submenu
                pass
            
            elif choice == 3:
                borrow_menu = {
                    '1': 'Borrow Book',
                    '2': 'Return Book',
                    '3': 'Back to Main Menu'
                }
                
                while True:
                    self.clear_screen()
                    self.print_menu(borrow_menu, "Borrow/Return Books")
                    
                    sub_choice = self.get_input("Enter your choice: ", int)
                    
                    if sub_choice == 1:
                        self.borrow_book_menu()
                    elif sub_choice == 2:
                        self.return_book_menu()
                    elif sub_choice == 3:
                        break
                    else:
                        print(Fore.RED + "Invalid choice. Please try again." + Style.RESET_ALL)
                        input("\nPress Enter to continue...")
            
            elif choice == 4:
                self.search_books_menu()
            
            elif choice == 5:
                self.clear_screen()
                self.display_statistics()
                input("\nPress Enter to continue...")
            
            elif choice == 6:
                self.view_member_history_menu()
            
            elif choice == 7:
                print(Fore.GREEN + "Thank you for using the Library Management System!" + Style.RESET_ALL)
                break
            
            else:
                print(Fore.RED + "Invalid choice. Please try again." + Style.RESET_ALL)
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    interface = LibraryInterface()
    interface.run()
