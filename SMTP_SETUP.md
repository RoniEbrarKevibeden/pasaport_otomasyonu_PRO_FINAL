# SMTP (E-posta) Kurulumu

Uygulama, parola sıfırlama bağlantısını e-posta ile göndermek için **smtplib** kullanır. Aşağıdaki ortam değişkenlerini ayarlayın (Windows PowerShell örneği):

```powershell
setx MAIL_ENABLED "true"
setx MAIL_SERVER "smtp.gmail.com"
setx MAIL_PORT "587"
setx MAIL_USERNAME "gmail-adresiniz@gmail.com"
setx MAIL_PASSWORD "Uygulama-Şifresi"
setx MAIL_USE_TLS "true"
setx MAIL_USE_SSL "false"
setx MAIL_FROM "Passport Automation <gmail-adresiniz@gmail.com>"
```

> **Gmail kullanıyorsanız:** 2 Adımlı Doğrulama (2FA) açın ve **App Password** (Uygulama Şifresi) oluşturun. Normal şifrenizi **kullanmayın**.

Kurulumdan sonra terminali kapatıp açın (yeni environment değişkenleri için) ve uygulamayı çalıştırın.
