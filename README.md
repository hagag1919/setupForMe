# setupForMe

`setupForMe` is a powerful tool designed to simplify the setup process for new computers by managing and configuring development programs and saving browser passwords. This app is ideal for developers who frequently set up new machines and need to quickly configure their development environments.

## Features

- **Password Management:** Automatically retrieves and saves browser passwords.
- **Setup Automation:** Allows users to add and configure apps (e.g., GitHub, Visual Studio) during the setup process.
- **Secure Storage:** Uses encryption to protect sensitive data and passwords.
- **Cross-Browser Support:** Currently supports Microsoft Edge, with plans to expand to other browsers.

## How It Works

1. **Retrieve Master Key:** The app extracts the master key from the browser's local state file.
2. **Decrypt Passwords:** It decrypts saved passwords from the browser's database using the retrieved master key.
3. **Save Encrypted Data:** Encrypted login data is stored in a secure file.
4. **Browser Configuration:** Allows the addition of new login data to the browser’s database.
5. **Secure Key Management:** Encryption keys are managed and stored securely using Windows Credential Manager.

## Requirements

- Python 3.x
- Required Python packages:
  - `pycryptodomex`
  - `cryptography`
  - `pypiwin32`

## Usage

1. **Run the App:** Execute the script to start the setup process.
2. **Configure Browsers:** Ensure the supported browsers (e.g., Microsoft Edge) are installed.
3. **Setup Apps:** Add the apps you want to configure.
4. **Retrieve & Save Passwords:** The app will handle the extraction, encryption, and saving of browser passwords.

## Code Overview

- **File Management:** Handles the copying and modification of browser database files.
- **Encryption:** Utilizes AES and Fernet for secure password storage and retrieval.
- **Database Interaction:** Uses SQLite for manipulating browser login data.

## Future Enhancements

- Support for additional browsers.
- Improved user interface for easier configuration and management.
- Expanded app integration and setup options.