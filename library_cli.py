import json
import uuid
from datetime import datetime, timedelta
from app import LibraryManagementSystem, Book, Member, Transaction

def display_menu():
    print("\nLibrary Management System")
    print("1. Add New Book")
    print("2. Add New Member")
    print("3. Borrow Book")
    print("4. Return Book")
    print("5. View All Books")
    print("6. View All Members")
    print("7. Exit")

def main():
    library = LibraryManagementSystem()

    while True:
        display_menu()
        choice = input("Select an option: ")

        if choice == '1':
            title = input("Enter book title: ")
            author = input("Enter author: ")
            isbn = input("Enter ISBN: ")
            genre = input("Enter genre: ")
            total_copies = int(input("Enter total copies: "))
            book_id = str(uuid.uuid4())[:8]
            book = Book(book_id, title, author, isbn, genre, total_copies)
            library.books[book_id] = book
            library.save_data()
            print(f"Book '{title}' added successfully.")

        elif choice == '2':
            name = input("Enter member name: ")
            email = input("Enter email: ")
            phone = input("Enter phone: ")
            member_id = str(uuid.uuid4())[:8]
            member = Member(member_id, name, email, phone)
            library.members[member_id] = member
            library.save_data()
            print(f"Member '{name}' added successfully.")

        elif choice == '3':
            member_id = input("Enter member ID: ")
            book_id = input("Enter book ID: ")
            if member_id in library.members and book_id in library.books:
                member = library.members[member_id]
                book = library.books[book_id]
                if member.is_active and book.available_copies > 0:
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
                    print(f"Book '{book.title}' borrowed successfully.")
                else:
                    print("Cannot borrow book. Check member status or book availability.")
            else:
                print("Invalid member or book ID.")

        elif choice == '4':
            transaction_id = input("Enter transaction ID: ")
            if transaction_id in library.transactions:
                transaction = library.transactions[transaction_id]
                if transaction.return_date is None:
                    transaction.return_date = datetime.now()
                    book = library.books[transaction.book_id]
                    book.available_copies += 1
                    book.is_available = True
                    member = library.members[transaction.member_id]
                    member.borrowed_books.remove(transaction_id)
                    library.save_data()
                    print("Book returned successfully.")
                else:
                    print("Book already returned.")
            else:
                print("Invalid transaction ID.")

        elif choice == '5':
            print("Books in the library:")
            for book in library.books.values():
                print(f"{book.title} by {book.author} (Available: {book.available_copies})")

        elif choice == '6':
            print("Members of the library:")
            for member in library.members.values():
                print(f"{member.name} (Email: {member.email}, Phone: {member.phone})")

        elif choice == '7':
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
