openssl pkcs12 -in .\ie.p12 -nocerts -out converted_ie.key -legacy -nodes
openssl pkcs12 -in .\ie.p12 -clcerts -nokeys -out converted_ie.crt -legacy

# 验证私钥
openssl rsa -in converted_ie.key -text -noout

# 验证证书
openssl x509 -in converted_ie.crt -text -noout
