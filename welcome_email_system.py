#!/usr/bin/env python3
"""
PayCrypt Gateway Welcome Email System
Sends professional onboarding emails to new clients
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

class PayCryptWelcomeEmail:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        
    def create_welcome_email(self, client_name, client_email, language='en', package_name='Starter'):
        """Create welcome email content"""
        
        # Email content by language
        content = {
            'en': {
                'subject': f"Welcome to PayCrypt Gateway, {client_name}! 🚀",
                'greeting': f"Dear {client_name},",
                'welcome_text': """
Welcome to PayCrypt Gateway! We're excited to help you integrate cryptocurrency payments into your platform.

Your account has been successfully created with our <strong>{package_name}</strong> package. You now have access to:

• Real-time crypto payment processing
• Multi-currency support (BTC, ETH, USDT, and more)
• Advanced security with HMAC verification
• Professional API with comprehensive documentation
• Multi-language support (EN, TR, RU)
• 24/7 technical support

<h3>🚀 Quick Start Guide</h3>

1. <strong>Access Your Dashboard:</strong> <a href="https://paycrypt.online/dashboard">Login to your dashboard</a>
2. <strong>Generate API Keys:</strong> Go to API Management → Generate Keys
3. <strong>Review Documentation:</strong> Download the attached integration guide
4. <strong>Test Integration:</strong> Use our sandbox environment for testing
5. <strong>Go Live:</strong> Switch to production when ready

<h3>📚 Resources Included</h3>

• Complete integration guide (attached PDF)
• API documentation and examples  
• SDK packages for Python and JavaScript
• Postman collection for API testing
• Sample code and best practices

<h3>💼 Enterprise Support</h3>

As a valued client, you have access to our technical support team:
• Email: support@paycrypt.online
• Response time: < 4 hours for your package tier
• Integration assistance available

<h3>🔧 Next Steps</h3>

1. Download and review the attached documentation
2. Set up your API keys in the dashboard
3. Test the integration in sandbox mode
4. Schedule a technical review call if needed

We're here to ensure your integration is smooth and successful. Don't hesitate to reach out with any questions!

Best regards,<br/>
The PayCrypt Gateway Team<br/>
support@paycrypt.online<br/>
https://paycrypt.online
                """,
                'footer': """
<hr style="border: 1px solid #eee; margin: 20px 0;">
<small style="color: #666;">
This email was sent to {client_email} because you created a PayCrypt Gateway account. 
If you didn't create this account, please contact us immediately at support@paycrypt.online.
</small>
                """
            },
            'tr': {
                'subject': f"PayCrypt Gateway'e Hoş Geldiniz, {client_name}! 🚀",
                'greeting': f"Sayın {client_name},",
                'welcome_text': """
PayCrypt Gateway'e hoş geldiniz! Kripto para ödemelerini platformunuza entegre etmenizde size yardımcı olmaktan heyecan duyuyoruz.

Hesabınız <strong>{package_name}</strong> paketi ile başarıyla oluşturuldu. Artık şunlara erişiminiz var:

• Gerçek zamanlı kripto ödeme işleme
• Çoklu para birimi desteği (BTC, ETH, USDT ve daha fazlası)
• HMAC doğrulama ile gelişmiş güvenlik
• Kapsamlı dokümantasyonlu profesyonel API
• Çok dilli destek (EN, TR, RU)
• 7/24 teknik destek

<h3>🚀 Hızlı Başlangıç Kılavuzu</h3>

1. <strong>Panonuza Erişin:</strong> <a href="https://paycrypt.online/dashboard">Panonuza giriş yapın</a>
2. <strong>API Anahtarları Oluşturun:</strong> API Yönetimi → Anahtar Oluştur
3. <strong>Dokümantasyonu İnceleyin:</strong> Ekteki entegrasyon kılavuzunu indirin
4. <strong>Entegrasyonu Test Edin:</strong> Test için sandbox ortamımızı kullanın
5. <strong>Canlıya Alın:</strong> Hazır olduğunuzda üretime geçin

<h3>📚 Dahil Edilen Kaynaklar</h3>

• Komple entegrasyon kılavuzu (ekteki PDF)
• API dokümantasyonu ve örnekler
• Python ve JavaScript için SDK paketleri
• API testi için Postman koleksiyonu
• Örnek kod ve en iyi uygulamalar

<h3>💼 Kurumsal Destek</h3>

Değerli bir müşteri olarak, teknik destek ekibimize erişiminiz var:
• E-posta: support@paycrypt.online
• Yanıt süresi: Paket seviyeniz için < 4 saat
• Entegrasyon yardımı mevcut

<h3>🔧 Sonraki Adımlar</h3>

1. Ekteki dokümantasyonu indirin ve inceleyin
2. Panoda API anahtarlarınızı ayarlayın
3. Sandbox modunda entegrasyonu test edin
4. Gerekirse teknik inceleme görüşmesi planlayın

Entegrasyonunuzun sorunsuz ve başarılı olmasını sağlamak için buradayız. Herhangi bir sorunuz olursa çekinmeden bizimle iletişime geçin!

En iyi dileklerimizle,<br/>
PayCrypt Gateway Ekibi<br/>
support@paycrypt.online<br/>
https://paycrypt.online
                """,
                'footer': """
<hr style="border: 1px solid #eee; margin: 20px 0;">
<small style="color: #666;">
Bu e-posta {client_email} adresine PayCrypt Gateway hesabı oluşturduğunuz için gönderildi.
Bu hesabı siz oluşturmadıysanız, lütfen derhal support@paycrypt.online adresinden bizimle iletişime geçin.
</small>
                """
            }
        }
        
        email_content = content.get(language, content['en'])
        
        # Create HTML email
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: #1a365d; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 30px; max-width: 600px; margin: 0 auto; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; }}
        a {{ color: #3182ce; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .cta-button {{ 
            display: inline-block; 
            background: #3182ce; 
            color: white; 
            padding: 12px 24px; 
            border-radius: 6px; 
            text-decoration: none; 
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PayCrypt Gateway</h1>
        <p>Enterprise Crypto Payment Solution</p>
    </div>
    
    <div class="content">
        <p>{email_content['greeting']}</p>
        
        {email_content['welcome_text'].format(package_name=package_name)}
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://paycrypt.online/dashboard" class="cta-button">
                Access Your Dashboard
            </a>
        </div>
        
        {email_content['footer'].format(client_email=client_email)}
    </div>
</body>
</html>
        """
        
        return {
            'subject': email_content['subject'],
            'html_body': html_body,
            'text_body': self.html_to_text(html_body)
        }
        
    def html_to_text(self, html):
        """Convert HTML to plain text"""
        import re
        # Simple HTML to text conversion
        text = re.sub('<[^<]+?>', '', html)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
        
    def send_welcome_email(self, client_name, client_email, language='en', 
                          package_name='Starter', attach_pdf=True):
        """Send welcome email with optional PDF attachment"""
        
        try:
            # Create email content
            email_data = self.create_welcome_email(client_name, client_email, language, package_name)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = os.getenv('MAIL_USERNAME', 'noreply@paycrypt.online')
            msg['To'] = client_email
            msg['Subject'] = email_data['subject']
            
            # Add text and HTML parts
            part1 = MIMEText(email_data['text_body'], 'plain', 'utf-8')
            part2 = MIMEText(email_data['html_body'], 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Attach PDF if requested
            if attach_pdf:
                pdf_filename = self.find_latest_launch_kit_pdf(language)
                if pdf_filename and os.path.exists(pdf_filename):
                    with open(pdf_filename, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= PayCrypt_Integration_Guide_{language.upper()}.pdf'
                    )
                    msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(
                os.getenv('MAIL_USERNAME', ''), 
                os.getenv('MAIL_PASSWORD', '')
            )
            
            text = msg.as_string()
            server.sendmail(msg['From'], client_email, text)
            server.quit()
            
            print(f"✅ Welcome email sent to {client_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send welcome email: {str(e)}")
            return False
            
    def find_latest_launch_kit_pdf(self, language):
        """Find the latest launch kit PDF for the given language"""
        import glob
        pattern = f"PayCrypt_Launch_Kit_{language.upper()}_*.pdf"
        files = glob.glob(pattern)
        if files:
            return max(files, key=os.path.getctime)  # Return newest file
        return None

def main():
    """Test the welcome email system"""
    
    # Test configuration
    test_clients = [
        {
            'name': 'John Smith',
            'email': 'test@example.com',  # Change to your email for testing
            'language': 'en',
            'package': 'Professional'
        },
        {
            'name': 'Ahmet Yılmaz', 
            'email': 'test2@example.com',  # Change to your email for testing
            'language': 'tr',
            'package': 'Enterprise'
        }
    ]
    
    print("🚀 Testing PayCrypt Welcome Email System...")
    
    welcome_system = PayCryptWelcomeEmail()
    
    for client in test_clients:
        print(f"\n📧 Generating welcome email for {client['name']} ({client['language']})...")
        
        # Just generate the email content (don't actually send)
        email_data = welcome_system.create_welcome_email(
            client['name'], 
            client['email'], 
            client['language'],
            client['package']
        )
        
        print(f"✅ Email generated:")
        print(f"   Subject: {email_data['subject']}")
        print(f"   Language: {client['language']}")
        print(f"   Package: {client['package']}")
        
        # Save HTML preview
        preview_filename = f"welcome_email_preview_{client['language']}.html"
        with open(preview_filename, 'w', encoding='utf-8') as f:
            f.write(email_data['html_body'])
        print(f"   Preview saved: {preview_filename}")
    
    print("\n🎉 Welcome email system ready!")
    print("\n📋 To send actual emails:")
    print("1. Set MAIL_USERNAME and MAIL_PASSWORD in your .env")
    print("2. Update test email addresses above")
    print("3. Call send_welcome_email() instead of create_welcome_email()")

if __name__ == '__main__':
    main()
