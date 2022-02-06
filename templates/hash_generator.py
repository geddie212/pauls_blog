from werkzeug.security import generate_password_hash, check_password_hash

password_hash = generate_password_hash(password='qwerty', method='sha512', salt_length=10)

hash_check = check_password_hash(pwhash=password_hash, password='qwerty')

print(password_hash)
print(hash_check)