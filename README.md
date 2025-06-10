# Halo

Halo is a command-line password manager available for **Linux, MacOS and Windows**.
Halo stores your passwords after encryption which can only be accessed by the
user.

Halo encrypts the passwords using the [Argon2id](https://github.com/p-h-c/phc-winner-argon2)
KDF hash function which was also the winner of [Password Hashing Competition
2015](https://password-hashing.net). It is a cryptographically secure password
hashing function that prevents brute-force attacks which still retaining the
normal benefits of encryption and salting. It was the highest reccomended KDF
for password hashing [Open Worldwide Application Security Project](owasp.org)
in 2023.

## How does it work?

For user authentication, Halo never stores the user password. It merely stores
a hash after a series of hashes and salts and encryptions which can be used to
authenticate the user by repeating the process at the time of login and
comparing the hashes. This guarantees absolute security for the user.

For the passwords, they are randomly generated and cryptographically safe
through the computers own entropy and noise from the hardware. A hash of this
password (**password hash**) is stored by Halo. After the user authenticates
himself, a **vault key** retrieved from the **master password hash** of the
user's password and the **vault key** is used to decrypt the **password hash**.

## Installation

### Requirements

Make sure to have the latest python version installed and mysql installed on
your computer.

### Installation Process

Clone this repository to the directory of your choice using the following command:

```
git clone https://github.com/AnshumanNeon/halo.git [path to the directory]
```

### Alternative Installation Process

Download this repository as a zip file and unzip it in a directory of your
choice.

### Post-Installation (Important)

1. Open the Halo folder (or `cd` into it) where all the python source code
   resides.

2. Create a file named `.env`

3. Using a text editor of your choice, enter the following details into the
   file:
   
   ```
   MYSQL_USER = [your mysql username]
   MYSQL_PASSWORD = [your mysql password]
   ```
   
   It is important to follow the format provided.
   
4. Save the file.

## Usage

After installation, open a terminal and `cd` to the folder where Halo is
installed. Then run the following command:

```
$ python ./main.py
```
