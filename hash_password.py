from werkzeug.security import generate_password_hash

# Generate a hashed password
password = 'admin123'  # Change this to your desired password
hashed_password = generate_password_hash(
    password,
    method='pbkdf2:sha256',
    salt_length=8
)

print(f"Hashed password: {hashed_password}")
