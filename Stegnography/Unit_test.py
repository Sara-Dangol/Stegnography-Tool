import unittest
import mysql.connector
import bcrypt
import os
from PIL import Image
from stegano import lsb
from InvisiData import connect_db, AuthApp, SteganoApp  


class TestSteganographyApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the database connection before all tests."""
        try:
            cls.db = connect_db()
            cls.cursor = cls.db.cursor()
        except Exception as e:
            raise Exception(f"Database connection error: {e}")

    def setUp(self):
        """Set up a test user before each test."""
        self.test_username = "test_user"
        self.test_password = "test_pass"
        hashed_password = bcrypt.hashpw(self.test_password.encode(), bcrypt.gensalt()).decode("utf-8")

        try:
            self.cursor.execute("DELETE FROM users WHERE username = %s", (self.test_username,))
            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)", (self.test_username, hashed_password)
            )
            self.db.commit()
        except mysql.connector.Error as e:
            self.fail(f"Database setup error: {e}")

    def test_user_registration(self):
        """Test user registration by inserting a new user after ensuring uniqueness."""
        username = "new_user"
        password = "new_pass"
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")

        try:
            self.cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            self.db.commit()

            self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            self.db.commit()
        except mysql.connector.Error as e:
            self.fail(f"User registration error: {e}")

        self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = self.cursor.fetchone()
        self.assertIsNotNone(user, "User registration failed!")

    def test_user_login(self):
        """Test user login by checking password hash."""
        self.cursor.execute("SELECT password FROM users WHERE username = %s", (self.test_username,))
        user = self.cursor.fetchone()
        self.assertIsNotNone(user, "User not found in database!")

        stored_hashed_password = user[0].encode("utf-8")
        self.assertTrue(bcrypt.checkpw(self.test_password.encode(), stored_hashed_password), "Password mismatch!")

    def test_hide_message_in_image(self):
        """Test hiding and revealing a message in an image using steganography."""
        test_image_path = "test_image.png"
        hidden_message = "Secret Message"

        img = Image.new("RGB", (100, 100), color=(255, 0, 0))
        img.save(test_image_path)

        if not os.path.exists(test_image_path):
            self.fail("Test image creation failed!")

        secret = lsb.hide(test_image_path, hidden_message)
        output_path = "hidden_test.png"
        secret.save(output_path)

        if not os.path.exists(output_path):
            self.fail("Hidden image file was not created!")

        revealed_message = lsb.reveal(output_path)
        self.assertEqual(hidden_message, revealed_message, "Steganography message retrieval failed!")

        for file in [test_image_path, output_path]:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                print(f"Error deleting {file}: {e}")

    def tearDown(self):
        """Clean up the database after each test."""
        try:
            self.cursor.execute("DELETE FROM users WHERE username = %s", (self.test_username,))
            self.db.commit()
        except mysql.connector.Error as e:
            print(f"Error in cleanup: {e}")

    @classmethod
    def tearDownClass(cls):
        """Close the database connection after all tests."""
        try:
            cls.cursor.close()
            cls.db.close()
        except mysql.connector.Error as e:
            print(f"Error closing database connection: {e}")


if __name__ == "__main__":
    unittest.main()

