import jwt

encoded = jwt.encode({"some": "payload"}, "secret", algorithm="HS256")
print(encoded)

decoded = jwt.decode(encoded, "secret", algorithms=["HS256"])
print(decoded)