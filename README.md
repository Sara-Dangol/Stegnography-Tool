🕵️‍♂️ Steganography Tool with Authentication 🔐

Welcome to the Steganography Tool! This tool allows you to hide and reveal messages inside images using LSB (Least Significant Bit) steganography. It also features user authentication with MySQL database integration, supporting both GUI and CLI modes. 🚀

📌 Features

✅ User Authentication: Register/Login with MySQL-based credential storage.✅ GUI Mode: A Tkinter-powered interface for easy use. 🎨✅ CLI Mode: Command-line interface for power users. 💻✅ Secure Message Hiding: Encrypts messages into images using LSB steganography. 🔏✅ Retrieve Hidden Messages: Extract hidden text from images effortlessly. 🕵️‍♀️✅ Cross-Platform: Works on Windows, Linux (Kali), and macOS. 🎯

⚙️ Installation & Setup

1️⃣ Install Dependencies

Ensure you have Python 3.x installed, then run:

pip install -r requirements.txt

2️⃣ Setup MySQL Database

You need XAMPP MySQL (or any MySQL server). Run the following SQL commands in your MySQL terminal:

CREATE DATABASE steganography_db; USE steganography_db; CREATE TABLE users ( id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL ); CREATE TABLE messages ( id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, image_path VARCHAR(255), hidden_message TEXT, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE );

🔹 Tip: You can use phpMyAdmin in XAMPP to execute these queries easily.

3️⃣ Run the Application

GUI Mode 🖥️

python sft.py

CLI Mode 🖥️

python sft.py --cli

🎮 Usage Guide

🔑 Authentication

Register a new user if you don’t have an account.

Login using your credentials.

🎭 Hiding a Message

Select an image (PNG/JPG).

Enter the message you want to hide.

Click “Hide” – The image will be saved with the hidden message.

🕵️ Revealing a Message

Open an image with hidden text.

Click “Show” – The hidden message will be displayed.

🛠️ Troubleshooting

❌ Error: Cannot connect to MySQL?

Ensure MySQL is running and credentials are correct.

Try mysql -u root -p and check if the database exists.

❌ Python Import Errors?

Run pip install -r requirements.txt to install missing packages.

❌ Steganography not working?

Ensure the image format is supported (PNG, JPG).

Try another image with better quality and resolution.

🎯 Future Enhancements

✅ AES Encryption for added security 🔐✅ Support for more image formats (BMP, GIF) 🖼️✅ Cloud database support ☁️

📜 License

MIT License © 2025 Sara
