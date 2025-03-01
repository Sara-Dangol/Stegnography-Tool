import mysql.connector
import bcrypt
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from stegano import lsb

# Database Configuration
DB_NAME = "steganography_db"
TABLE_MESSAGES = "messages"
TABLE_USERS = "users"

def connect_db():
    """Connect to MySQL and create the database and tables if they don't exist."""
    conn = mysql.connector.connect(
        host="localhost",
        user="root",  
        password=""
    )
    cursor = conn.cursor()

    try:

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.database = DB_NAME

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_USERS} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        cursor.execute("DROP TABLE IF EXISTS messages")

        cursor.execute(f"""
            CREATE TABLE messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                image_path VARCHAR(255),
                hidden_message TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
    finally:
        cursor.close()  # Close the cursor to prevent sync issues

    return conn


def open_steganography_tool(user_id):
    root = tk.Tk()
    app = SteganoApp(root, user_id)
    root.mainloop()


class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login/Register")
        self.root.geometry('400x300')
        self.db = connect_db()
        icon_path = os.path.abspath("./logo_resized.png")  
        icon_image = tk.PhotoImage(file=icon_path)
        root.iconphoto(False, icon_image)

        tk.Label(root, text="User Authentication", font=("Arial", 16, "bold")).pack(pady=10)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        tk.Label(root, text="Username").pack()
        self.entry_username = tk.Entry(root, textvariable=self.username_var)
        self.entry_username.pack()

        tk.Label(root, text="Password").pack()
        self.entry_password = tk.Entry(root, textvariable=self.password_var, show="*")
        self.entry_password.pack()

        self.btn_login = tk.Button(root, text="Login", command=self.login)
        self.btn_login.pack(pady=5)

        self.btn_register = tk.Button(root, text="Register", command=self.register)
        self.btn_register.pack(pady=5)

    def register(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and Password are required!")
            return

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8') 

        try:
            cursor = self.db.cursor()
            cursor.execute(f"INSERT INTO {TABLE_USERS} (username, password) VALUES (%s, %s)", (username, hashed_password))
            self.db.commit()
            cursor.close()
            messagebox.showinfo("Success", "User registered successfully!")
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")


    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and Password are required!")
            return

        cursor = self.db.cursor()
        cursor.execute(f"SELECT id, password FROM {TABLE_USERS} WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode(), user[1].encode('utf-8')):
            messagebox.showinfo("Success", "Login successful!")
            self.root.destroy()  
            open_steganography_tool(user[0])  
        else:
            messagebox.showerror("Error", "Invalid credentials!")


class SteganoApp:
    def __init__(self, root, user_id):  
        self.root = root
        self.user_id = user_id 
        self.root.title("Steganography Tool")
        self.root.geometry('700x500')
        self.root.configure(bg='white')

        icon_path = os.path.abspath("./img.png")  
        icon_image = tk.PhotoImage(file=icon_path)
        root.iconphoto(False, icon_image)

        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Image", command=self.open_image)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

        tk.Label(self.root, text="Steganography Tool", font=("Arial", 20, "bold"), bg="white").pack(pady=10)

        self.frame_image = tk.Frame(self.root, bg="gray", width=340, height=280, relief=tk.GROOVE)
        self.frame_image.place(x=10, y=80)
        self.lbl_image = tk.Label(self.frame_image, bg="gray")
        self.lbl_image.place(x=40, y=10)

        self.frame_text = tk.Frame(self.root, width=340, height=280, bg="white", relief=tk.GROOVE)
        self.frame_text.place(x=350, y=80)
        self.text_box = tk.Text(self.frame_text, font="Arial 12", bg="white", fg="black")
        self.text_box.place(x=0, y=0, width=320, height=270)

        self.frame_controls = tk.Frame(self.root, bg="white")
        self.frame_controls.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

        self.btn_open = self.create_button("Open Image", self.open_image)
        self.btn_hide = self.create_button("Hide", self.hide_message)
        self.btn_show = self.create_button("Show", self.reveal_message)

        self.btn_open.grid(row=0, column=0, padx=10)
        self.btn_hide.grid(row=0, column=1, padx=10)
        self.btn_show.grid(row=0, column=2, padx=10)

        self.filename = None
        self.db = connect_db()  


        self.filename = None
        self.db = connect_db()  

    def create_button(self, text, command):
        btn = tk.Button(
            self.frame_controls, text=text, width=12, height=2, font="Arial 12 bold",
            bg="#007BFF", fg="white", activebackground="#0056b3", activeforeground="white",
            relief=tk.RAISED, bd=3, command=command
        )
        btn.bind("<Enter>", lambda e: btn.config(bg="#0056b3"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#007BFF"))
        return btn

    def open_image(self):
        self.filename = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg")])
        if self.filename:
            img = Image.open(self.filename).resize((250, 250), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            self.lbl_image.configure(image=img)
            self.lbl_image.image = img

    def hide_message(self):
        if not self.filename:
            messagebox.showerror("Error", "Select an image first!")
            return

        message = self.text_box.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Error", "Enter a message to hide!")
            return

        try:
            img = Image.open(self.filename)
            secret = lsb.hide(img, message)  # Embed the message
            output_path = os.path.join(os.path.dirname(self.filename), "hidden.png")
            secret.save(output_path)  # Save the modified image

            cursor = self.db.cursor()
            cursor.execute(f"INSERT INTO {TABLE_MESSAGES} (user_id, image_path, hidden_message) VALUES (%s, %s, %s)",
                        (self.user_id, output_path, message))
            self.db.commit()
            cursor.close()

            self.text_box.delete("1.0", tk.END)
            messagebox.showinfo("Success", f"Message hidden successfully in {output_path}!")

        except Exception as e:
            messagebox.showerror("Error", f"Error hiding message: {e}")



    def reveal_message(self):
        if not self.filename:
            messagebox.showerror("Error", "Select an image first!")
            return

        try:
            img = Image.open(self.filename)
            hidden_message = lsb.reveal(img)  # Extract hidden message

            if hidden_message:
                self.text_box.delete("1.0", tk.END)
                self.text_box.insert(tk.END, hidden_message)
                messagebox.showinfo("Success", "Message retrieved successfully!")
            else:
                messagebox.showerror("Error", "No hidden message found in the image!")

        except Exception as e:
            messagebox.showerror("Error", f"Error retrieving message: {e}")


def CLI():
    db = connect_db()
    cursor = db.cursor()
    
    print("Welcome to CLI Steganography Tool")
    print("1. Login\n2. Register")
    choice = input("Select an option: ")
    
    if choice == "1":
        username = input("Enter username: ")
        password = input("Enter password: ")
        cursor.execute(f"SELECT id, password FROM {TABLE_USERS} WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode(), user[1].encode('utf-8')):
            print("Login successful!")
            user_id = user[0]
        else:
            print("Invalid credentials!")
            return
    
    elif choice == "2":
        username = input("Enter username: ")
        password = input("Enter password: ")
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
        
        try:
            cursor.execute(f"INSERT INTO {TABLE_USERS} (username, password) VALUES (%s, %s)", (username, hashed_password))
            db.commit()
            print("User registered successfully!")
            user_id = cursor.lastrowid
        except mysql.connector.IntegrityError:
            print("Username already exists!")
            return
    else:
        print("Invalid option!")
        return
    
    while True:
        print("\n1. Hide message\n2. Reveal message\n3. Exit")
        option = input("Choose an option: ")
        
        if option == "1":
            image_path = input("Enter image path: ").strip()
            message = input("Enter message to hide: ").strip()
            output_path = os.path.join(os.path.dirname(image_path), "hidden_cli.png")

            try:
                img = Image.open(image_path)
                secret = lsb.hide(img, message)  # Hide message in image
                secret.save(output_path)  # Save modified image

                cursor.execute(f"""
                    INSERT INTO {TABLE_MESSAGES} (user_id, image_path, hidden_message)
                    VALUES (%s, %s, %s)
                """, (user_id, output_path, message))
                db.commit()

                print(f"Message successfully hidden in {output_path}")

            except Exception as e:
                print(f"Error hiding message: {e}")


        elif option == "2":
            image_path = input("Enter image path: ").strip()

            try:
                img = Image.open(image_path)
                hidden_message = lsb.reveal(img)  # Extract hidden message

                if hidden_message:
                    print(f"Hidden message: {hidden_message}")
                else:
                    print("No hidden message found in the image!")

            except Exception as e:
                print(f"Error revealing message: {e}")

        elif option == "3":
            print("Exiting CLI mode...")
            break

        else:
            print("Invalid option!")

if __name__ == "__main__":
    mode = input("Choose mode: (1) GUI (2) CLI: ")
    if mode == "1":
        print("Launching GUI...")
        root = tk.Tk()
        app = AuthApp(root)
        root.mainloop()
    elif mode == "2":
        cli = CLI()
        cli.login()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    root = tk.Tk()
    app = AuthApp(root)
    root.mainloop()
