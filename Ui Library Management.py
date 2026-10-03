import streamlit as st
import json
import random
import string
from pathlib import Path
from datetime import datetime


# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# LIBRARY CLASS
# =========================================================

class Library:

    database = Path(__file__).parent / "library.json"

    data = {
        "books": [],
        "member": []
    }

    # -----------------------------------------------------
    # LOAD DATABASE
    # -----------------------------------------------------

    @classmethod
    def load_data(cls):

        if cls.database.exists():

            try:

                with open(cls.database, "r") as f:

                    content = f.read().strip()

                    if content:
                        cls.data = json.loads(content)

                    else:
                        cls.data = {
                            "books": [],
                            "member": []
                        }

            except json.JSONDecodeError:

                cls.data = {
                    "books": [],
                    "member": []
                }

        else:

            cls.data = {
                "books": [],
                "member": []
            }

            cls.save_data()

    # -----------------------------------------------------
    # SAVE DATABASE
    # -----------------------------------------------------

    @classmethod
    def save_data(cls):

        with open(cls.database, "w") as f:

            json.dump(
                cls.data,
                f,
                indent=4
            )

    # -----------------------------------------------------
    # GENERATE ID
    # -----------------------------------------------------

    @staticmethod
    def gen_id(prefix="B"):

        random_id = ""

        for i in range(5):

            random_id += random.choice(
                string.ascii_uppercase + string.digits
            )

        return prefix + "_" + random_id

    # -----------------------------------------------------
    # ADD BOOK
    # -----------------------------------------------------

    @classmethod
    def add_book(cls, title, author, copies):

        book = {

            "id": cls.gen_id("B"),

            "title": title,

            "author": author,

            "total_copies": copies,

            "available_copies": copies,

            "added_on":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
        }

        cls.data["books"].append(book)

        cls.save_data()

        return book

    # -----------------------------------------------------
    # ADD MEMBER
    # -----------------------------------------------------

    @classmethod
    def add_member(cls, name, email):

        member = {

            "id": cls.gen_id("M"),

            "name": name,

            "email": email,

            "borowed": []
        }

        cls.data["member"].append(member)

        cls.save_data()

        return member

    # -----------------------------------------------------
    # BORROW BOOK
    # -----------------------------------------------------

    @classmethod
    def borrow_book(cls, member_id, book_id):

        members = [
            m for m in cls.data["member"]
            if m["id"] == member_id
        ]

        if not members:
            return False, "Member does not exist."

        member = members[0]

        books = [
            b for b in cls.data["books"]
            if b["id"] == book_id
        ]

        if not books:
            return False, "Book does not exist."

        book = books[0]

        if book["available_copies"] <= 0:
            return False, "No copy of this book is available."

        # Check if member already borrowed same book
        already_borrowed = any(
            b["book_id"] == book_id
            for b in member["borowed"]
        )

        if already_borrowed:
            return False, "This member already has this book."

        borrow_entry = {

            "book_id": book["id"],

            "title": book["title"],

            "borrow_on":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
        }

        member["borowed"].append(
            borrow_entry
        )

        book["available_copies"] -= 1

        cls.save_data()

        return True, "Book borrowed successfully."

    # -----------------------------------------------------
    # RETURN BOOK
    # -----------------------------------------------------

    @classmethod
    def return_book(cls, member_id, book_id):

        members = [
            m for m in cls.data["member"]
            if m["id"] == member_id
        ]

        if not members:
            return False, "Member does not exist."

        member = members[0]

        borrowed_book = None

        for book in member["borowed"]:

            if book["book_id"] == book_id:

                borrowed_book = book

                break

        if borrowed_book is None:

            return False, "This book is not borrowed by this member."

        member["borowed"].remove(
            borrowed_book
        )

        books = [
            b for b in cls.data["books"]
            if b["id"] == book_id
        ]

        if books:

            books[0]["available_copies"] += 1

        cls.save_data()

        return True, "Book returned successfully."


# =========================================================
# LOAD DATA
# =========================================================

Library.load_data()


# =========================================================
# HEADER
# =========================================================

st.title("📚 Library Management System")

st.caption(
    "A simple Library Management System built with Python, OOP, JSON & Streamlit"
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📚 Library Menu")

menu = st.sidebar.radio(
    "Select Operation",
    [
        "🏠 Dashboard",
        "➕ Add Book",
        "📚 List Books",
        "👤 Add Member",
        "👥 List Members",
        "📖 Borrow Book",
        "↩️ Return Book",
        "🔎 Search Book"
    ]
)


# =========================================================
# DATA
# =========================================================

books = Library.data["books"]

members = Library.data["member"]


# =========================================================
# DASHBOARD
# =========================================================

if menu == "🏠 Dashboard":

    st.header("🏠 Dashboard")

    total_books = len(books)

    total_copies = sum(
        book["total_copies"]
        for book in books
    )

    available_copies = sum(
        book["available_copies"]
        for book in books
    )

    borrowed_copies = (
        total_copies - available_copies
    )

    total_members = len(members)

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📚 Book Titles",
            total_books
        )

    with col2:

        st.metric(
            "📦 Total Copies",
            total_copies
        )

    with col3:

        st.metric(
            "✅ Available",
            available_copies
        )

    with col4:

        st.metric(
            "👥 Members",
            total_members
        )

    st.divider()

    st.subheader("📊 Library Statistics")

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            f"📖 Currently Borrowed: {borrowed_copies}"
        )

    with col2:

        st.success(
            f"📗 Available Books: {available_copies}"
        )

    st.divider()

    st.subheader("📚 Recent Books")

    if books:

        for book in books[-5:]:

            st.write(
                f"**{book['title']}** — "
                f"{book['author']} "
                f"({book['available_copies']}/"
                f"{book['total_copies']} available)"
            )

    else:

        st.warning("No books available.")


# =========================================================
# ADD BOOK
# =========================================================

elif menu == "➕ Add Book":

    st.header("➕ Add New Book")

    with st.form("add_book_form"):

        title = st.text_input(
            "Book Title",
            placeholder="Enter book title"
        )

        author = st.text_input(
            "Author",
            placeholder="Enter author name"
        )

        copies = st.number_input(
            "Number of Copies",
            min_value=1,
            value=1,
            step=1
        )

        submit = st.form_submit_button(
            "➕ Add Book"
        )

        if submit:

            if not title.strip():

                st.error(
                    "Please enter book title."
                )

            elif not author.strip():

                st.error(
                    "Please enter author name."
                )

            else:

                book = Library.add_book(
                    title.strip(),
                    author.strip(),
                    copies
                )

                st.success(
                    f"Book added successfully! "
                    f"Book ID: {book['id']}"
                )


# =========================================================
# LIST BOOKS
# =========================================================

elif menu == "📚 List Books":

    st.header("📚 All Books")

    if not books:

        st.warning(
            "No books found."
        )

    else:

        for book in books:

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [4, 3, 2]
                )

                with col1:

                    st.subheader(
                        f"📖 {book['title']}"
                    )

                    st.write(
                        f"Author: {book['author']}"
                    )

                    st.caption(
                        f"Book ID: {book['id']}"
                    )

                with col2:

                    st.write(
                        f"📦 Total Copies: "
                        f"{book['total_copies']}"
                    )

                    st.write(
                        f"✅ Available: "
                        f"{book['available_copies']}"
                    )

                with col3:

                    if book["available_copies"] > 0:

                        st.success(
                            "Available"
                        )

                    else:

                        st.error(
                            "Not Available"
                        )


# =========================================================
# ADD MEMBER
# =========================================================

elif menu == "👤 Add Member":

    st.header("👤 Add New Member")

    with st.form("member_form"):

        name = st.text_input(
            "Member Name",
            placeholder="Enter member name"
        )

        email = st.text_input(
            "Email",
            placeholder="Enter email"
        )

        submit = st.form_submit_button(
            "➕ Add Member"
        )

        if submit:

            if not name.strip():

                st.error(
                    "Please enter member name."
                )

            elif not email.strip():

                st.error(
                    "Please enter email."
                )

            else:

                member = Library.add_member(
                    name.strip(),
                    email.strip()
                )

                st.success(
                    f"Member added successfully! "
                    f"Member ID: {member['id']}"
                )


# =========================================================
# LIST MEMBERS
# =========================================================

elif menu == "👥 List Members":

    st.header("👥 Library Members")

    if not members:

        st.warning(
            "No members found."
        )

    else:

        for member in members:

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [3, 4, 3]
                )

                with col1:

                    st.subheader(
                        f"👤 {member['name']}"
                    )

                    st.caption(
                        f"ID: {member['id']}"
                    )

                with col2:

                    st.write(
                        f"📧 {member['email']}"
                    )

                with col3:

                    st.write(
                        f"📚 Borrowed: "
                        f"{len(member['borowed'])}"
                    )

                if member["borowed"]:

                    st.write(
                        "📖 Borrowed Books:"
                    )

                    for borrowed in member["borowed"]:

                        st.write(
                            f"- {borrowed['title']} "
                            f"({borrowed['book_id']})"
                        )


# =========================================================
# BORROW BOOK
# =========================================================

elif menu == "📖 Borrow Book":

    st.header("📖 Borrow Book")

    if not members:

        st.warning(
            "First add a member."
        )

    elif not books:

        st.warning(
            "First add a book."
        )

    else:

        member_options = {
            f"{m['name']} ({m['id']})":
            m["id"]
            for m in members
        }

        book_options = {
            f"{b['title']} "
            f"({b['id']}) - "
            f"{b['available_copies']} available":
            b["id"]
            for b in books
            if b["available_copies"] > 0
        }

        if not book_options:

            st.error(
                "No books are currently available."
            )

        else:

            selected_member = st.selectbox(
                "👤 Select Member",
                list(member_options.keys())
            )

            selected_book = st.selectbox(
                "📖 Select Book",
                list(book_options.keys())
            )

            if st.button(
                "📖 Borrow Book",
                type="primary"
            ):

                member_id = member_options[
                    selected_member
                ]

                book_id = book_options[
                    selected_book
                ]

                success, message = Library.borrow_book(
                    member_id,
                    book_id
                )

                if success:

                    st.success(message)

                    st.rerun()

                else:

                    st.error(message)


# =========================================================
# RETURN BOOK
# =========================================================

elif menu == "↩️ Return Book":

    st.header("↩️ Return Book")

    members_with_books = [
        m for m in members
        if m["borowed"]
    ]

    if not members_with_books:

        st.info(
            "No member currently has a borrowed book."
        )

    else:

        member_options = {
            f"{m['name']} ({m['id']})":
            m["id"]
            for m in members_with_books
        }

        selected_member = st.selectbox(
            "👤 Select Member",
            list(member_options.keys())
        )

        member_id = member_options[
            selected_member
        ]

        selected_member_data = next(
            m for m in members
            if m["id"] == member_id
        )

        borrowed_books = selected_member_data[
            "borowed"
        ]

        book_options = {
            f"{book['title']} ({book['book_id']})":
            book["book_id"]
            for book in borrowed_books
        }

        selected_book = st.selectbox(
            "📖 Select Book",
            list(book_options.keys())
        )

        if st.button(
            "↩️ Return Book",
            type="primary"
        ):

            book_id = book_options[
                selected_book
            ]

            success, message = Library.return_book(
                member_id,
                book_id
            )

            if success:

                st.success(message)

                st.rerun()

            else:

                st.error(message)


# =========================================================
# SEARCH BOOK
# =========================================================

elif menu == "🔎 Search Book":

    st.header("🔎 Search Books")

    search = st.text_input(
        "Search by book title or author",
        placeholder="Type something..."
    )

    if search:

        search = search.lower()

        results = [

            book
            for book in books

            if search in book["title"].lower()
            or search in book["author"].lower()
        ]

        if results:

            st.success(
                f"{len(results)} book(s) found."
            )

            for book in results:

                with st.container(border=True):

                    st.subheader(
                        f"📖 {book['title']}"
                    )

                    st.write(
                        f"Author: {book['author']}"
                    )

                    st.write(
                        f"Book ID: {book['id']}"
                    )

                    st.write(
                        f"Available: "
                        f"{book['available_copies']} / "
                        f"{book['total_copies']}"
                    )

        else:

            st.warning(
                "No matching book found."
            )