from jwcrypto import jwk

KTY = ''
SIZE = 0
ALG = ''
USE = ''
KID = ''

key = jwk.JWK.generate(kty=KTY, size=SIZE, alg=ALG, use=USE, kid=KID)
public_key = key.export_public()
private_key = key.export_private()

with open('public_key.json', 'w') as f:
    f.write(public_key)
with open('private_key.json', 'w') as f:
    f.write(private_key)
