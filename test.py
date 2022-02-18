from werkzeug.security import check_password_hash, generate_password_hash

correct_password = '1234'
wrong_password = '1234'

hashed_correct_password = generate_password_hash(correct_password)
hashed_wrong_password = generate_password_hash(wrong_password)
