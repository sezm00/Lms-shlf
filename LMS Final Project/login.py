import tkinter as tk
from tkinter import messagebox as tkmb
import customtkinter as ctk
from customtkinter import set_default_color_theme
import time
import random
import pandas as pd
import bcrypt
from datetime import datetime, timedelta
import main

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

    def user_authentication(self, username, user_id, password):
        for _, row in self.admin_data_df.iterrows():
            if (row['Username'] == username or row['ID'] == user_id) and bcrypt.checkpw(password.encode(), row['Password'].encode()):
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
            if (row['Membership ID'] == username or row['Member Name'] == username) and bcrypt.checkpw(password.encode(), str(row['Password']).encode()):
                return "member"
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

set_default_color_theme("custom_theme.json")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")

        self.frame = ctk.CTkFrame(master=self)
        self.frame.pack(pady=127, padx=237, fill='both', expand=1)
        
        self.user = User()
        self.member = Member()

        self.login_widgets()
        
    def login_widgets(self):
       
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        login_custom_font = ("Inter", 32)

        label = ctk.CTkLabel(master=self.frame, text='Login', font=login_custom_font)
        label.pack(pady=12, padx=10)

        self.username_entry = ctk.CTkEntry(master=self.frame, width=253, height=21, placeholder_text="Username")
        self.username_entry.pack(pady=30, padx=10)

        self.password_entry = ctk.CTkEntry(master=self.frame, width=253, height=21, placeholder_text="Password", show='*')
        self.password_entry.pack(pady=1, padx=10)

        login_button = ctk.CTkButton(master=self.frame, width=86, height=21, text="Login", command=self.login_event)
        login_button.pack(pady=30, padx=10)

        signup_button = ctk.CTkButton(master=self.frame, width=86, height=21, text="Sign Up", fg_color='#E5383B', command=self.signup_widgets)
        signup_button.pack(pady=10, padx=10)
        
    def signup_widgets(self):
       
        for widget in self.frame.winfo_children():
            widget.destroy()
                
        signup_custom_font = ("Inter", 32)

        label = ctk.CTkLabel(master=self.frame, text='Signup', font=signup_custom_font)
        label.pack(pady=19, padx=10)

        self.name_new_entry = ctk.CTkEntry(master=self.frame, width=253, height=21, placeholder_text="Full Name")
        self.name_new_entry.pack(pady=1, padx=10)

        self.username_new_entry = ctk.CTkEntry(master=self.frame, width=253, height=21, placeholder_text="Username")
        self.username_new_entry.pack(pady=30, padx=10)

        self.password_new_entry = ctk.CTkEntry(master=self.frame, width=253, height=21, placeholder_text="Password", show='*')
        self.password_new_entry.pack(pady=1, padx=10)

        signup_button = ctk.CTkButton(master=self.frame, width=86, height=21, text="Sign Up", command=self.signup_event)
        signup_button.pack(pady=20, padx=10)

        login_button = ctk.CTkButton(master=self.frame, width=86, height=21, text="Login", fg_color='#E5383B', command=self.login_widgets)
        login_button.pack(pady=1, padx=10)
    
    
    def login_event(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        

        user_type = self.user.user_authentication(username, username, password)
        if not user_type:
            user_type = self.member.member_authentication(username, password)

        if user_type:
            
            app.destroy()
            main.run(username, user_type)
        else:
            
            tkmb.showerror("Error", "Invalid username or password.")

    def signup_event(self):
        name = self.name_new_entry.get()
        username = self.username_new_entry.get()
        password = self.password_new_entry.get()
        
        if self.member.add_member(name, password):
           
            app.destroy()
            main.run(username, "user")
        else:
            tkmb.showerror("Error", "Signup failed.")

if __name__ == "__main__":
    app = App()
    app.geometry("770x550")
    app.title("Shlf")
    app.maxsize(770, 550)
    app.mainloop()
