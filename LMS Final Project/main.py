import time
import random
from tkinter import Toplevel, ttk
import pandas as pd
import bcrypt
import tkinter as tk
from tkinter import messagebox as tkmb
import customtkinter as ctk
from customtkinter import set_default_color_theme
from datetime import datetime, timedelta

set_default_color_theme("custom_theme.json")

class User:
    def __init__(self):
        self.admin_csv = 'admins.csv'
        self.admin_data_df = self._read_admins()

    def _read_admins(self):
        try:
            return pd.read_csv(self.admin_csv)
        except FileNotFoundError:
            print("Admins file not found.")
            return pd.DataFrame(columns=['ID', 'Username', 'Password', 'UserType'])

    def _write_admins(self):
        self.admin_data_df.to_csv(self.admin_csv, index=False)

    def change_password(self, user_id, username, new_password):
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        user_found = False
        for i, row in self.admin_data_df.iterrows():
            if row['ID'] == user_id and row['Username'] == username:
                self.admin_data_df.at[i, 'Password'] = hashed_password
                user_found = True

        if not user_found:
            return False

        self._write_admins()
        return True

    def add_user(self, new_user_id, new_username, new_password, user_type):
        if self.admin_data_df['ID'].eq(new_user_id).any() or self.admin_data_df['Username'].eq(new_username).any():
            return False

        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

        new_user = {
            'ID': new_user_id,
            'Username': new_username,
            'Password': hashed_password,
            'UserType': user_type
        }

        self.admin_data_df = pd.concat([self.admin_data_df, pd.DataFrame([new_user])], ignore_index=True)
        self._write_admins()
        return True

    def user_authentication(self, username, password):
        for _, row in self.admin_data_df.iterrows():
            if row['Username'] == username:
                if bcrypt.checkpw(password.encode(), row['Password'].encode()):
                    return row['UserType']
        return False

    def update_user(self, user_id, new_username=None, new_password=None, new_user_type=None):
        user_found = False
        for i, row in self.admin_data_df.iterrows():
            if row['ID'] == user_id:
                if new_username:
                    self.admin_data_df.at[i, 'Username'] = new_username
                if new_password:
                    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                    self.admin_data_df.at[i, 'Password'] = hashed_password
                if new_user_type:
                    self.admin_data_df.at[i, 'UserType'] = new_user_type
                user_found = True

        if not user_found:
            return False

        self._write_admins()
        return True

    def delete_user(self, user_id):
        initial_count = len(self.admin_data_df)
        self.admin_data_df = self.admin_data_df[self.admin_data_df['ID'] != user_id]

        if len(self.admin_data_df) == initial_count:
            return False

        self._write_admins()
        return True

    def search_user(self, search_term):
        search_result = self.admin_data_df[(self.admin_data_df['ID'].str.contains(search_term, case=False)) |
                                           (self.admin_data_df['Username'].str.contains(search_term, case=False)) |
                                           (self.admin_data_df['UserType'].str.contains(search_term, case=False))]
        return search_result if not search_result.empty else None

    def count_users(self, user_type=None):
        if user_type:
            return len(self.admin_data_df[self.admin_data_df['UserType'] == user_type])
        return len(self.admin_data_df)


class Member:
    def __init__(self):
        self.members_csv = 'members.csv'
        self.members_data_df = self._read_members()

    def _read_members(self):
        try:
            return pd.read_csv(self.members_csv)
        except FileNotFoundError:
            print("Members file not found.")
            return pd.DataFrame(columns=['Membership ID', 'Member Name', 'Borrowed Books', 'Fine', 'Password'])

    def _write_members(self):
        self.members_data_df.to_csv(self.members_csv, index=False)

    def member_authentication(self, username, password):
        for _, row in self.members_data_df.iterrows():
            if row['Membership ID'] == username or row['Member Name'] == username:
                if bcrypt.checkpw(password.encode(), row['Password'].encode()):
                    return True
        return False

    def add_member(self, member_name, password):
        if (self.members_data_df['Member Name'] == member_name).any():
            return False

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        new_member = {
            'Membership ID': self.generate_unique_id(),
            'Member Name': member_name,
            'Borrowed Books': '',
            'Fine': 0,
            'Password': hashed_password
        }

        self.members_data_df = pd.concat([self.members_data_df, pd.DataFrame([new_member])], ignore_index=True)
        self._write_members()
        return True

    def generate_unique_id(self):
        timestamp = int(time.time() * 1000)
        random_num = random.randint(0, 1000)
        unique_id = str(timestamp) + str(random_num)
        unique_id = unique_id[:9].ljust(9, '0')
        return unique_id

    def update_member(self, member_id, new_member_name=None, new_password=None):
        member_found = False
        for i, row in self.members_data_df.iterrows():
            if row['Membership ID'] == member_id:
                if new_member_name:
                    self.members_data_df.at[i, 'Member Name'] = new_member_name
                if new_password:
                    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                    self.members_data_df.at[i, 'Password'] = hashed_password
                member_found = True

        if not member_found:
            return False

        self._write_members()
        return True

    def delete_member(self, member_id):
        initial_count = len(self.members_data_df)
        self.members_data_df = self.members_data_df[self.members_data_df['Membership ID'] != member_id]

        if len(self.members_data_df) == initial_count:
            return False

        self._write_members()
        return True

    def search_member(self, search_term):
        search_result = self.members_data_df[(self.members_data_df['Membership ID'].str.contains(search_term, case=False)) |
                                             (self.members_data_df['Member Name'].str.contains(search_term, case=False))]
        return search_result if not search_result.empty else None


class BookManager:
    def __init__(self, csv_file='books.csv', members_csv='Members.csv'):
        self.csv_file = csv_file
        self.members_csv = members_csv
        self.books_data_df = self._read_books()  # Initialize books data
        self.members_data_df = self._read_members()  # Initialize members data

    def _read_books(self):
        try:
            df = pd.read_csv(self.csv_file, dtype={'Date Borrowed': str, 'Date of Return': str})
            return df
        except FileNotFoundError:
            print("Books file not found.")
            return pd.DataFrame(columns=['Book Name', 'Author', 'Genre', 'Quantity', 'Borrowed', 'Date Borrowed', 'Date of Return'])

    def _write_books(self, books_data_df):
        books_data_df.to_csv(self.csv_file, index=False)
        self.books_data_df = books_data_df  # Update the instance attribute

    def _read_members(self):
        try:
            return pd.read_csv(self.members_csv)
        except FileNotFoundError:
            print("Members file not found.")
            return pd.DataFrame(columns=['Membership ID', 'Member Name', 'Borrowed Books', 'Fine'])

    def _write_members(self, members_data_df):
        members_data_df.to_csv(self.members_csv, index=False)
        self.members_data_df = members_data_df
        
    def borrow_book(self, membership_id, member_name, book_name, author):
        books_data_df = self._read_books()
        members_data_df = self._read_members()

        book = books_data_df.loc[(books_data_df['Book Name'] == book_name) & (books_data_df['Author'] == author) & (books_data_df['Quantity'] > 0)]
        member = members_data_df.loc[(members_data_df['Membership ID'] == membership_id) & (members_data_df['Member Name'] == member_name)]

        if not book.empty and not member.empty:
            book_idx = book.index[0]
            member_idx = member.index[0]

            books_data_df.at[book_idx, 'Borrowed'] += 1
            books_data_df.at[book_idx, 'Date Borrowed'] = datetime.now().strftime('%Y-%m-%d')
            books_data_df.at[book_idx, 'Date of Return'] = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            books_data_df.at[book_idx, 'Quantity'] -= 1

            borrowed_books = str(members_data_df.at[member_idx, 'Borrowed Books'])
            
            if pd.isna(borrowed_books):
                borrowed_books = []
            else:
                try:
                    borrowed_books = borrowed_books.split('|')
                except:
                    borrowed_books = borrowed_books
                    
            borrowed_books.append(book_name)
            members_data_df.at[member_idx, 'Borrowed Books'] = '|'.join(borrowed_books)

            self._write_books(books_data_df)
            self._write_members(members_data_df)
            return True

        return False


    def add_book(self, add_book_name, add_author, add_genre, quantity=1):
        books_data_df = self._read_books()

        book = books_data_df.loc[(books_data_df['Book Name'] == add_book_name) & (books_data_df['Author'] == add_author)]
        if not book.empty:
            book_idx = book.index[0]
            books_data_df.at[book_idx, 'Quantity'] += quantity
        else:
            new_book = {
                'Book Name': add_book_name,
                'Author': add_author,
                'Genre': add_genre,
                'Quantity': quantity,
                'Borrowed': 0,
                'Date Borrowed': '',
                'Date of Return': ''
                
            }
            books_data_df = pd.concat([books_data_df, pd.DataFrame([new_book])], ignore_index=True)
        
        self._write_books(books_data_df)
        return True
    
    
    def update_book(self, book_name,new_author=None, new_genre=None, new_quantity=None, new_Borrowed=None, new_date_borrowed=None, new_date_of_return=None):
            
            books_data_df = self._read_books()
            book_found = False

            for i, row in books_data_df.iterrows():
                if row['Book Name'] == book_name:
                    if book_name:
                        books_data_df.at[i, 'Book Name'] = book_name
                    if new_author:
                        books_data_df.at[i, 'Author'] = new_author
                    if new_genre:
                        books_data_df.at[i, 'Genre'] = new_genre
                    if new_quantity is not None: 
                        books_data_df.at[i, 'Quantity'] = new_quantity
                    if new_Borrowed:
                        books_data_df.at[i, 'Borrowed'] = new_Borrowed
                    if new_date_borrowed:
                        books_data_df.at[i, 'Date Borrowed'] = new_date_borrowed
                    if new_date_of_return:
                        books_data_df.at[i, 'Date of Return'] = new_date_of_return
                    book_found = True

            if not book_found:
                return False

            self._write_books(books_data_df)
            return True

    def return_book(self, membership_id, member_name, returned_book_name):
        books_data_df = self._read_books()
        members_data_df = self._read_members()

        membership_id = int(membership_id)

        book = books_data_df.loc[(books_data_df['Book Name'] == returned_book_name) & (books_data_df['Borrowed'] > 0)]
        member = members_data_df.loc[(members_data_df['Membership ID'] == membership_id) & (members_data_df['Member Name'] == member_name)]

        if not book.empty and not member.empty:
            book_idx = book.index[0]
            member_idx = member.index[0]

            return_date = datetime.strptime(books_data_df.at[book_idx, 'Date of Return'], '%Y-%m-%d')
            if datetime.now() > return_date:
                fine_amount = self._calculate_fine(books_data_df)
                if fine_amount > 0:
                    members_data_df.at[member_idx, 'Fine'] += fine_amount

            books_data_df.at[book_idx, 'Borrowed'] -= 1
            books_data_df.at[book_idx, 'Date Borrowed'] = ''
            books_data_df.at[book_idx, 'Date of Return'] = ''
            books_data_df.at[book_idx, 'Quantity'] += 1

            borrowed_books = members_data_df.at[member_idx, 'Borrowed Books']
            if pd.notna(borrowed_books):
                borrowed_books = borrowed_books.split('|')
                borrowed_books.remove(returned_book_name)
                members_data_df.at[member_idx, 'Borrowed Books'] = '|'.join(borrowed_books)

            self._write_books(books_data_df)
            self._write_members(members_data_df)

            return True

        return False

    
    def delete_book(self, book_name, author):
        initial_count = len(self.books_data_df)
        self.books_data_df = self.books_data_df[~((self.books_data_df['Book Name'] == book_name) & (self.books_data_df['Author'] == author))]

        if len(self.books_data_df) == initial_count:
            return False

        self._write_books(self.books_data_df)
        return True
    
    def _calculate_fine(self, books_data_df):
        total_fine = 0
        for _, book in books_data_df.iterrows():
            try:
                return_date = datetime.strptime(book['Date of Return'], '%Y-%m-%d')
                days_overdue = (datetime.now() - return_date).days
                if days_overdue > 0:
                    total_fine += days_overdue * 25  
            except (ValueError, TypeError):
               
                continue
        return total_fine



class LibraryApp(ctk.CTk):
    def __init__(self, username, type):
        super().__init__()
        self.title("Shlf")
        self.geometry("800x600")

        self.username = username
        self.type = type 
        self.user = User()
        self.member = Member()
        self.book_manager = BookManager()
        
        self.create_sidebar()
        self.create_dashboard()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=150, fg_color="#161A1D", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.username_label = ctk.CTkLabel(self.sidebar, text=f"Welcome\n{self.username}", anchor="w")
        self.username_label.pack(pady=10, padx=10)

        sidebar_buttons = []
        
        if self.type == "member":
            sidebar_buttons = [("Books", self.show_books_members)]
        elif self.type == "admin":
            sidebar_buttons = [("Dashboard", self.show_dashboard), ("Transaction", self.show_transaction), 
                               ("Books", self.show_books), ("Members", self.show_members), ("Users", self.show_users)]
        elif self.type in ["librarian", "stock manager"]:
            sidebar_buttons = [("Dashboard", self.show_dashboard), ("Transaction", self.show_transaction), 
                               ("Books", self.show_books), ("Members", self.show_members)]
        elif self.type == "stock":
            sidebar_buttons = [("Dashboard", self.show_dashboard), ("Books", self.show_books)]
            
        for btn_text, btn_command in sidebar_buttons:
            button = ctk.CTkButton(self.sidebar, width=150, height=30, text=btn_text, fg_color="#161A1D", corner_radius=0, command=btn_command)
            button.pack(fill="x", pady=5)

        self.logout_button = ctk.CTkButton(self.sidebar, text="Logout", corner_radius=0, fg_color="#161A1D", command=self.logout)
        self.logout_button.pack(side="bottom", fill="x", pady=5)

    def create_dashboard(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)
        if self.type == "member":
            self.show_books_members()
        else:
            self.show_dashboard()

    def show_dashboard(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.top_bar = ctk.CTkFrame(self.main_frame, height=50, fg_color='#E0E0E0')
        self.top_bar.pack(pady=10, padx=20, fill="x")

        self.dashboard_label = ctk.CTkLabel(self.top_bar, text="Dashboard", font=("Roboto", 24, "bold"), text_color='#BA181B', anchor="w")
        self.dashboard_label.pack(pady=10, padx=20, side="left")

        stats_frame = ctk.CTkFrame(self.main_frame, fg_color="#FFFFFF")
        stats_frame.pack(fill="both", expand=True, padx=20, pady=20)

        stats = [
            ("Total Books", self.book_manager._read_books()['Quantity'].sum()),
            ("Total Members", self.member._read_members().shape[0]),
            ("Currently Borrowed", self.book_manager._read_books()['Borrowed'].sum()),
            ("Total Fines", self.book_manager._read_members()['Fine'].sum())
        ]

        for i, (label, value) in enumerate(stats):
            stat_frame = ctk.CTkFrame(stats_frame, fg_color="#E5383B", height=100, width=150, corner_radius=10)
            stat_frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            stat_label = ctk.CTkLabel(stat_frame, text=str(value), font=("Roboto", 32), text_color="#FFFFFF")
            stat_label.pack(pady=(10, 0))

            stat_text = ctk.CTkLabel(stat_frame, text=label, font=("Roboto", 14), text_color="#FFFFFF")
            stat_text.pack()

        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)

        recently_added_frame = ctk.CTkFrame(stats_frame, fg_color="#F6F6F6", height=200)
        recently_added_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=20, sticky="nsew")

        recently_added_label = ctk.CTkLabel(recently_added_frame, text="Recently Added Books", font=("Roboto", 16), text_color="#000000")
        recently_added_label.pack(anchor="w", padx=10, pady=10)

        recently_added_books = self.book_manager._read_books().iloc[::-1].head(5)
        
        for _, book in recently_added_books.iterrows():
            book_label = ctk.CTkLabel(recently_added_frame, text=f"{book['Book Name']} by {book['Author']}", font=("Roboto", 14), text_color="#000000")
            book_label.pack(anchor="w", padx=10)

        recently_borrowed_frame = ctk.CTkFrame(stats_frame, fg_color="#F6F6F6", height=200)
        recently_borrowed_frame.grid(row=1, column=2, columnspan=2, padx=10, pady=20, sticky="nsew")

        recently_borrowed_label = ctk.CTkLabel(recently_borrowed_frame, text="Recently Borrowed Books", font=("Roboto", 16), text_color="#000000")
        recently_borrowed_label.pack(anchor="w", padx=10, pady=10)

        recently_borrowed_books = self.book_manager._read_books().sort_values(by='Date Borrowed', ascending=False).head(5)
        
        for _, book in recently_borrowed_books.iterrows():
            book_label = ctk.CTkLabel(recently_borrowed_frame, text=f"{book['Book Name']} by {book['Author']}", font=("Roboto", 14), text_color="#000000")
            book_label.pack(anchor="w", padx=10)

        stats_frame.grid_rowconfigure(1, weight=1)

    def show_transaction(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.top_bar = ctk.CTkFrame(self.main_frame, height=35, fg_color='#D1D1D1', corner_radius=22.5)
        self.top_bar.pack(pady=10, padx=20, fill="x")

        self.transaction_label = ctk.CTkLabel(self.top_bar, text="Transaction", font=("Roboto", 20), text_color='#BA181B', anchor="w")
        self.transaction_label.pack(pady=10, padx=20, side="left")

        self.transaction_frame = ctk.CTkFrame(self.main_frame, width=500, height=500, fg_color="#BA181B", corner_radius=20)
        self.transaction_frame.pack(expand=True, pady=20)

        self.membership_id_entry = ctk.CTkEntry(self.transaction_frame, width=235, height=21, placeholder_text="Membership ID", fg_color="#800000", text_color="#FFFFFF", border_width=2, border_color="#800000")
        self.membership_id_entry.pack(pady=10, padx=20)

        self.member_name_entry = ctk.CTkEntry(self.transaction_frame, width=235, height=21, placeholder_text="Member Name", fg_color="#800000", text_color="#FFFFFF", border_width=2, border_color="#800000")
        self.member_name_entry.pack(pady=10, padx=20)

        self.book_name_entry = ctk.CTkEntry(self.transaction_frame, width=235, height=21, placeholder_text="Book Name", fg_color="#800000", text_color="#FFFFFF", border_width=2, border_color="#800000")
        self.book_name_entry.pack(pady=10, padx=20)

        self.author_entry = ctk.CTkEntry(self.transaction_frame, width=235, height=21, placeholder_text="Author", fg_color="#800000", text_color="#FFFFFF", border_width=2, border_color="#800000")
        self.author_entry.pack(pady=10, padx=20)

        self.borrow_button = ctk.CTkButton(self.transaction_frame, width=150, height=21, text="Borrow", fg_color="#E5383B", text_color="#FFFFFF", hover_color="#BA181B", corner_radius=20, command=self.borrow_book)
        self.borrow_button.pack(pady=20)
        
        self.return_button = ctk.CTkButton(self.transaction_frame, width=150, height=21, text="Return", fg_color="#E5383B", text_color="#FFFFFF", hover_color="#BA181B", corner_radius=20, command=self.return_book)
        self.return_button.pack(pady=20)

    def borrow_book(self):
        membership_id = int(self.membership_id_entry.get())
        member_name = self.member_name_entry.get()
        book_name = str(self.book_name_entry.get())
        author = self.author_entry.get()
        
        success = self.book_manager.borrow_book(membership_id, member_name, book_name, author)
        if success:
            tkmb.showinfo("Success", "Book borrowed successfully.")
        else:
            tkmb.showerror("Error", "Failed to borrow book. Check details and availability.")

    def return_book(self):
        membership_id = int(self.membership_id_entry.get())
        member_name = self.member_name_entry.get()
        book_name = self.book_name_entry.get()
        
        success = self.book_manager.return_book(membership_id, member_name, book_name)
        if success:
            fine = self.member.get_fine(membership_id)
            if fine > 0:
                self.show_fine_payment_window(membership_id, fine)
            else:
                tkmb.showinfo("Success", "Book returned successfully.")
        else:
            tkmb.showerror("Error", "Failed to return book. Check details.")

    def show_fine_payment_window(self, membership_id, fine):
        fine_window = ctk.CTkToplevel(self)
        fine_window.title("Outstanding Fine")
        fine_window.geometry("300x200")

        fine_label = ctk.CTkLabel(fine_window, text=f"Member has an outstanding fine of {fine} EGP.", font=("Roboto", 14))
        fine_label.pack(pady=20)

        pay_button = ctk.CTkButton(fine_window, text="Pay Fine", command=lambda: self.pay_fine(membership_id, fine_window))
        pay_button.pack(pady=10)

    def pay_fine(self, membership_id, fine_window):
        self.member.pay_fine(membership_id)
        fine_window.destroy()
        tkmb.showinfo("Success", "Fine paid successfully. Book return completed.")

    def show_books(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.top_bar = ctk.CTkFrame(self.main_frame, height=35, fg_color='#D1D1D1', corner_radius=22.5)
        self.top_bar.pack(pady=10, padx=20, fill="x")

        self.books_label = ctk.CTkLabel(self.top_bar, text="Books", font=("Roboto", 20), text_color='#BA181B', anchor="w")
        self.books_label.pack(pady=10, padx=20, side="left")

        self.books_table_frame = ctk.CTkFrame(self.main_frame, fg_color="#D3D3D3")
        self.books_table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.book_columns = ["Book Name", "Author", "Genre", "Quantity","Borrowed","Date Borrowed","Date of Return"]
        self.book_table = ttk.Treeview(self.books_table_frame, columns=self.book_columns, show="headings")
        for column in self.book_columns:
            self.book_table.heading(column, text=column)
        self.book_table.pack(fill="both", expand=True)

        self.populate_book_table()

        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="#FFFFFF")
        self.button_frame.pack(fill="x", pady=10, padx=20, side="bottom")

        # Add button
        self.add_button = ctk.CTkButton(self.button_frame, width=114, height=28, text="Add", fg_color="#E5383B", command=self.add_book)
        self.add_button.pack(side="right", padx=10)

        # Update button
        self.edit_button = ctk.CTkButton(self.button_frame, width=114, height=28, text="Edit", fg_color="#E5383B", command=self.edit_book)
        self.edit_button.pack(side="right", padx=(10, 0))

        # Delete button
        self.delete_button = ctk.CTkButton(self.button_frame, width=114, height=28, text="Delete", fg_color="#E5383B", command=self.delete_book)
        self.delete_button.pack(side="right")

    def populate_book_table(self):
        self.book_table.delete(*self.book_table.get_children())
        books = self.book_manager._read_books()
        for _, book in books.iterrows():
            self.book_table.insert("", "end", values=book.tolist())

    def add_book(self):
        self.book_form_popup("Add Book", self.book_manager.add_book)

    def edit_book(self):
        selected_item = self.book_table.selection()
        if selected_item:
            book_details = self.book_table.item(selected_item)["values"]
            self.book_form_popup("Edit Book", self.book_manager.update_book, book_details)

    def delete_book(self):
        selected_item = self.book_table.selection()
        if selected_item:
            book_details = self.book_table.item(selected_item)["values"]
            self.book_manager.delete_book(book_details[0], book_details[1])
            self.populate_book_table()

  
    def book_form_popup(self, title, submit_func, book_details=None):
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("400x400")

        # Create a frame within the CTkToplevel to set the fg_color
        frame = ctk.CTkFrame(popup, fg_color="#E5383B")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        entries = {}
        fields = ["Book Name", "Author", "Genre", "Quantity"]

        if book_details:
            for i, field in enumerate(fields):
                ctk.CTkLabel(frame, text=field).pack(pady=5)
                entry = ctk.CTkEntry(frame, width=200)
                entry.insert(0, book_details[i])
                entry.pack(pady=5)
                entries[field] = entry
        else:
            for field in fields:
                ctk.CTkLabel(frame, text=field).pack(pady=5)
                entries[field] = ctk.CTkEntry(frame, width=200)
                entries[field].pack(pady=5)

        def submit():
            book_data = {field: entry.get() for field, entry in entries.items()}
            book_data["Quantity"] = int(book_data["Quantity"])
            if book_details:
                submit_func(book_data["Book Name"], book_data.get("Author"), book_data.get("Genre"), book_data.get("Quantity"))
            else:
                submit_func(book_data["Book Name"], book_data["Author"], book_data["Genre"], book_data["Quantity"])
            self.populate_book_table()
            popup.destroy()

        ctk.CTkButton(frame, text="Submit", command=submit).pack(pady=20)

    def show_books_members(self):
            for widget in self.main_frame.winfo_children():
                widget.destroy()

            self.top_bar = ctk.CTkFrame(self.main_frame, height=35, fg_color='#D1D1D1', corner_radius=22.5)
            self.top_bar.pack(pady=10, padx=20, fill="x")

            self.books_label = ctk.CTkLabel(self.top_bar, text="Books", font=("Roboto", 20), text_color='#BA181B', anchor="w")
            self.books_label.pack(pady=10, padx=20, side="left")

            self.books_table_frame = ctk.CTkFrame(self.main_frame, fg_color="#D3D3D3")
            self.books_table_frame.pack(fill="both", expand=True, padx=20, pady=20)

            self.book_columns = ["Book Name", "Author", "Genre", "Quantity","Borrowed","Date Borrowed","Date of Return"]
            self.book_table = ttk.Treeview(self.books_table_frame, columns=self.book_columns, show="headings")
            for column in self.book_columns:
                self.book_table.heading(column, text=column)
            self.book_table.pack(fill="both", expand=True)

            self.populate_book_member_table()

    def populate_book_member_table(self):
        self.book_table.delete(*self.book_table.get_children())
        books = self.book_manager._read_books()
        for _, book in books.iterrows():
            self.book_table.insert("", "end", values=book.tolist())
        
    def show_members(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.top_bar = ctk.CTkFrame(self.main_frame, height=35, fg_color='#D1D1D1', corner_radius=22.5)
        self.top_bar.pack(pady=10, padx=20, fill="x")

        self.members_label = ctk.CTkLabel(self.top_bar, text="Members", font=("Roboto", 20), text_color='#BA181B', anchor="w")
        self.members_label.pack(pady=10, padx=20, side="left")

        self.members_table_frame = ctk.CTkFrame(self.main_frame, fg_color="#D3D3D3")
        self.members_table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        member_columns = ["Membership ID", "Member Name", "Borrowed Books", "Fine"]
        self.member_table = ttk.Treeview(self.members_table_frame, columns=member_columns, show="headings")
        for column in member_columns:
            self.member_table.heading(column, text=column)
        self.member_table.pack(fill="both", expand=True)

        self.populate_member_table()

        self.member_button_frame = ctk.CTkFrame(self.main_frame, fg_color="#FFFFFF")
        self.member_button_frame.pack(fill="x", pady=10, padx=20, side="bottom")

            # Add button
        self.add_member_button = ctk.CTkButton(self.member_button_frame, width=114, height=28, text="Add", fg_color="#E5383B", command=self.add_member)
        self.add_member_button.pack(side="right", padx=(10, 0))

            # Edit button
        self.edit_member_button = ctk.CTkButton(self.member_button_frame, width=114, height=28, text="Edit", fg_color="#E5383B", command=self.edit_member)
        self.edit_member_button.pack(side="right", padx=(10, 0))

            # Delete button
        self.delete_member_button = ctk.CTkButton(self.member_button_frame, width=114, height=28, text="Delete", fg_color="#E5383B", command=self.delete_member)
        self.delete_member_button.pack(side="right")

    def populate_member_table(self):
            self.member_table.delete(*self.member_table.get_children())
            members = self.member._read_members()
            for _, member in members.iterrows():
                self.member_table.insert("", "end", values=member.tolist())

    def add_member(self):
            self.member_form_popup("Add Member", self.member.add_member)

    def edit_member(self):
            selected_item = self.member_table.selection()
            if selected_item:
                member_details = self.member_table.item(selected_item)["values"]
                self.member_form_popup("Edit Member", self.member.update_member, member_details)

    def delete_member(self):
            selected_item = self.member_table.selection()
            if selected_item:
                member_details = self.member_table.item(selected_item)["values"]
                self.member.delete_member(member_details[0])
                self.populate_member_table()

    def member_form_popup(self, title, submit_func, member_details=None):
            popup = ctk.CTkToplevel(self)
            popup.title(title)
            popup.geometry("400x400")

            entries = {}
            fields = ["Membership ID", "Member Name", "Password"]
            if member_details:
                for i, field in enumerate(fields):
                    ctk.CTkLabel(popup, text=field).pack(pady=5)
                    entry = ctk.CTkEntry(popup, width=200)
                    entry.insert(0, member_details[i])
                    entry.pack(pady=5)
                    entries[field] = entry
            else:
                for field in fields:
                    ctk.CTkLabel(popup, text=field).pack(pady=5)
                    entries[field] = ctk.CTkEntry(popup, width=200)
                    entries[field].pack(pady=5)

            def submit():
                member_data = {field: entry.get() for field, entry in entries.items()}
                if member_details:
                    submit_func(member_data["Membership ID"], member_data["Member Name"], member_data["Password"])
                else:
                    submit_func(member_data["Member Name"], member_data["Password"])
                self.populate_member_table()
                popup.destroy()

            ctk.CTkButton(popup, text="Submit", command=submit).pack(pady=20)

    def show_users(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.top_bar = ctk.CTkFrame(self.main_frame, height=35, fg_color='#D1D1D1', corner_radius=22.5)
        self.top_bar.pack(pady=10, padx=20, fill="x")

        self.users_label = ctk.CTkLabel(self.top_bar, text="Users", font=("Roboto", 20), text_color='#BA181B', anchor="w")
        self.users_label.pack(pady=10, padx=20, side="left")

        self.users_table_frame = ctk.CTkFrame(self.main_frame, fg_color="#D3D3D3")
        self.users_table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        user_columns = ["ID", "Username", "UserType"]
        self.user_table = ttk.Treeview(self.users_table_frame, columns=user_columns, show="headings")
        for column in user_columns:
            self.user_table.heading(column, text=column)
        self.user_table.pack(fill="both", expand=True)

        self.populate_user_table()

        self.user_button_frame = ctk.CTkFrame(self.main_frame, fg_color="#FFFFFF")
        self.user_button_frame.pack(fill="x", pady=10, padx=20, side="bottom")

        # Add button
        self.add_user_button = ctk.CTkButton(self.user_button_frame, width=114, height=28, text="Add", fg_color="#E5383B", command=self.add_user)
        self.add_user_button.pack(side="right", padx=(10, 0))

        # Edit button
        self.edit_user_button = ctk.CTkButton(self.user_button_frame, width=114, height=28, text="Edit", fg_color="#E5383B", command=self.edit_user)
        self.edit_user_button.pack(side="right", padx=(10, 0))

        # Delete button
        self.delete_user_button = ctk.CTkButton(self.user_button_frame, width=114, height=28, text="Delete", fg_color="#E5383B", command=self.delete_user)
        self.delete_user_button.pack(side="right")

    def populate_user_table(self):
        self.user_table.delete(*self.user_table.get_children())
        users =self.user._read_admins()
        for _, user in users.iterrows():
            self.user_table.insert("", "end", values=user.tolist())

    def add_user(self):
        self.user_form_popup("Add User", self.user.add_user)

    def edit_user(self):
        selected_item = self.user_table.selection()
        if selected_item:
            user_details = self.user_table.item(selected_item)["values"]
            self.user_form_popup("Edit User", self.user.update_user, user_details)

    def delete_user(self):
        selected_item = self.user_table.selection()
        if selected_item:
            user_details = self.user_table.item(selected_item)["values"]
            self.user.delete_user(user_details[0])
            self.populate_user_table()

    def user_form_popup(self, title, submit_func, user_details=None):
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("400x400")

        entries = {}
        fields = ["Username", "Password", "UserType"]
        if user_details:
            for i, field in enumerate(fields):
                ctk.CTkLabel(popup, text=field).pack(pady=5)
                entry = ctk.CTkEntry(popup, width=200)
                entry.insert(0, user_details[i + 1])
                entry.pack(pady=5)
                entries[field] = entry
        else:
            for field in fields:
                ctk.CTkLabel(popup, text=field).pack(pady=5)
                entries[field] = ctk.CTkEntry(popup, width=200)
                entries[field].pack(pady=5)

        def submit():
            user_data = {field: entry.get() for field, entry in entries.items()}
            if user_details:
                submit_func(user_details[0], user_data["Username"], user_data["Password"], user_data["UserType"])
            else:
                submit_func(user_data["Username"], user_data["Password"], user_data["UserType"])
            self.populate_user_table()
            popup.destroy()

        ctk.CTkButton(popup, text="Submit", command=submit).pack(pady=20)
    def logout(self):
        self.destroy()


def run(username, type):
    app = LibraryApp(username, type)
    app.mainloop()