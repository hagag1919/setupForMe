import os
import sqlite3
import shutil
import base64
import json
from Cryptodome.Cipher import AES  # Adjusted for pycryptodomex
import time
from win32crypt import CryptUnprotectData
from urllib.parse import urlparse
from cryptography.fernet import Fernet
import win32cred

# Paths for various browsers
appdata = os.getenv('LOCALAPPDATA')
browsers = {
    'msedge': appdata + '\\Microsoft\\Edge\\User Data',
}

data_queries = {
    'login_data': {
        'query': 'SELECT action_url, username_value, password_value FROM logins',
        'file': '\\Login Data',
        'columns': ['URL', 'Email', 'Password'],
        'decrypt': True
    }
}


# Function to retrieve master key from the browser's Local State file
def get_master_key(path: str):
    with open(path + "\\Local State", "r", encoding="utf-8") as f:
        local_state = json.loads(f.read())
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    return CryptUnprotectData(key, None, None, None, 0)[1]


# Function to decrypt the passwords stored in the browser's database
def decrypt_password(buff: bytes, key: bytes) -> str:
    if isinstance(buff, str):
        try:
            buff = bytes.fromhex(buff)
        except ValueError:
            print(f"Invalid hexadecimal string: {buff}")
            return ""
    iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt(payload)
    return decrypted_pass[:-16].decode()


# Function to extract login data from the browser
def get_login_data(path: str, profile: str, key):
    db_file = f'{path}\\{profile}\\Login Data'
    shutil.copy(db_file, 'temp_login_db')
    conn = sqlite3.connect('temp_login_db')
    cursor = conn.cursor()
    cursor.execute(data_queries['login_data']['query'])
    result = []
    for row in cursor.fetchall():
        url, username, password = row
        if password:
            password = decrypt_password(password, key)
        result.append((url, username, password))
    conn.close()
    os.remove('temp_login_db')
    return result


# Generate or retrieve encryption key from Windows Credential Manager
def get_encryption_key(target_name):
    try:
        credential = win32cred.CredRead(Type=win32cred.CRED_TYPE_GENERIC, TargetName=target_name)
        key = base64.b64decode(credential['CredentialBlob'])
    except Exception:
        # Generate a new key if none exists and store it
        key = Fernet.generate_key()
        win32cred.CredWrite({
            'Type': win32cred.CRED_TYPE_GENERIC,
            'TargetName': target_name,
            'CredentialBlob': base64.b64encode(key).decode(),  # decode bytes to string
            'Persist': win32cred.CRED_PERSIST_LOCAL_MACHINE
        })
    return key


# Encrypt and save the login data to a file
def save_encrypted_login_data(login_data, key, filename='encrypted_logins.json'):
    cipher_suite = Fernet(key)
    encrypted_data = []
    for url, username, password in login_data:
        encrypted_username = cipher_suite.encrypt(username.encode('utf-8')).decode('utf-8')
        encrypted_password = cipher_suite.encrypt(password.encode('utf-8')).decode('utf-8')
        encrypted_data.append({
            "url": url,
            "encrypted_username": encrypted_username,
            "encrypted_password": encrypted_password
        })

    with open(filename, 'w') as file:
        json.dump(encrypted_data, file)


# Save login data to a browser's database
def save_login_data_to_browser(url: str, username: str, password: str, path: str, profile: str, key):
    # Copy the Login Data file to a temporary location
    db_file = f'{path}\\{profile}\\Login Data'
    shutil.copy(db_file, 'temp_login_db')

    # Encrypt the password using the master key
    iv = os.urandom(12)
    cipher = AES.new(key, AES.MODE_GCM, iv)
    encrypted_password = cipher.encrypt(password.encode('utf-8')) + cipher.digest()

    # Get the scheme from the url
    scheme = urlparse(url).scheme

    # Open the copied database and insert the new login data
    conn = sqlite3.connect('temp_login_db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO logins (origin_url, action_url, username_value, password_value, date_created, signon_realm, blacklisted_by_user, scheme) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (url, url, username, base64.b64encode(iv + encrypted_password).decode('utf-8'),
         int(time.time() * 1000000), url, 0, scheme)  # Use time.time() instead of datetime.utcnow()
    )
    conn.commit()
    conn.close()

    # Add a delay
    time.sleep(1)

    # Replace the original Login Data file with the modified one
    shutil.move('temp_login_db', db_file)
    print(f"Saved login data for {url} to browser's database.")


# Decrypt and read back the credentials from the file
def decrypt_login_data(filename, key):
    cipher_suite = Fernet(key)
    with open(filename, 'r') as file:
        encrypted_data = json.load(file)

    decrypted_data = []
    for entry in encrypted_data:
        decrypted_username = cipher_suite.decrypt(entry['encrypted_username'].encode('utf-8')).decode('utf-8')
        decrypted_password = cipher_suite.decrypt(entry['encrypted_password'].encode('utf-8')).decode('utf-8')
        decrypted_data.append((entry['url'], decrypted_username, decrypted_password))

    return decrypted_data


# Main execution
if __name__ == '__main__':
    browser = 'msedge'
    profile = 'Default'
    browser_path = browsers[browser]
    master_key = get_master_key(browser_path)

    # Get login data from Edge
    login_data = get_login_data(browser_path, profile, master_key)

    # Get or generate encryption key
    encryption_key_name = 'MyEdgeEncryptionKey'
    encryption_key = get_encryption_key(encryption_key_name)

    # Save encrypted login data to a file
   # save_encrypted_login_data(login_data, encryption_key)

    # Decrypt and read back the login data
    #decrypted_login_data = decrypt_login_data('encrypted_logins.json', encryption_key)
   # for url, username, password in decrypted_login_data:
    #    print(f"URL: {url}, Username: {username}, Password: {password}")
