import jwt
import random

key_length = 1024
key = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(key_length))
print(key)

encoded = jwt.encode({"some": "payload"}, key, algorithm="HS256")
print(encoded)

decoded = jwt.decode(encoded, key, algorithms=["HS256"])
print(decoded)