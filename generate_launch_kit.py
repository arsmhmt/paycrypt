#!/usr/bin/env python3
"""
PayCrypt Gateway Client Launch Kit PDF Generator
Creates professional documentation for enterprise clients
"""

import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, white, blue
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors

class PayCryptLaunchKitPDF:
    def __init__(self, language='en'):
        self.language = language
        self.colors = {
            'primary': HexColor('#1a365d'),      # Dark blue
            'secondary': HexColor('#2d3748'),    # Dark gray
            'accent': HexColor('#3182ce'),       # Blue
            'success': HexColor('#38a169'),      # Green
            'warning': HexColor('#d69e2e'),      # Orange
            'light': HexColor('#f7fafc'),        # Light gray
        }
        
        # Content in different languages
        self.content = {
            'en': {
                'title': 'PayCrypt Gateway',
                'subtitle': 'Enterprise Crypto Payment Solution',
                'welcome_title': 'Welcome to PayCrypt Gateway',
                'welcome_text': '''
                Thank you for choosing PayCrypt Gateway as your crypto payment solution. 
                This comprehensive guide will help you integrate our advanced payment system 
                into your platform and start accepting cryptocurrency payments immediately.
                
                PayCrypt Gateway offers enterprise-grade security, multi-currency support, 
                real-time processing, and comprehensive analytics to power your crypto payment needs.
                ''',
                'features_title': 'Key Features',
                'features': [
                    'Real-time crypto payment processing',
                    'Multi-currency support (BTC, ETH, USDT, and more)',
                    'Advanced security with HMAC verification',
                    'Webhook integration for instant notifications',
                    'Comprehensive API with rate limiting',
                    'Multi-language support (EN, TR, RU)',
                    'Enterprise-grade analytics and reporting',
                    'Dedicated technical support'
                ],
                'plans_title': 'Service Plans Comparison',
                'api_title': 'API Integration Guide',
                'sdk_title': 'SDK Documentation',
                'security_title': 'Security & Compliance',
                'support_title': 'Technical Support & Resources',
                'onboarding_title': 'Quick Start Guide',
                'contact_title': 'Contact Information'
            },
            'tr': {
                'title': 'PayCrypt Gateway',
                'subtitle': 'Kurumsal Kripto Ödeme Çözümü',
                'welcome_title': 'PayCrypt Gateway\'e Hoş Geldiniz',
                'welcome_text': '''
                Kripto ödeme çözümünüz olarak PayCrypt Gateway\'i tercih ettiğiniz için teşekkür ederiz.
                Bu kapsamlı kılavuz, gelişmiş ödeme sistemimizi platformunuza entegre etmenize
                ve kripto para ödemelerini hemen kabul etmeye başlamanıza yardımcı olacaktır.
                
                PayCrypt Gateway, kurumsal düzeyde güvenlik, çoklu para birimi desteği,
                gerçek zamanlı işleme ve kapsamlı analitik sunar.
                ''',
                'features_title': 'Temel Özellikler',
                'features': [
                    'Gerçek zamanlı kripto ödeme işleme',
                    'Çoklu para birimi desteği (BTC, ETH, USDT ve daha fazlası)',
                    'HMAC doğrulama ile gelişmiş güvenlik',
                    'Anında bildirimler için webhook entegrasyonu',
                    'Hız sınırlı kapsamlı API',
                    'Çok dilli destek (EN, TR, RU)',
                    'Kurumsal düzeyde analitik ve raporlama',
                    'Özel teknik destek'
                ],
                'plans_title': 'Hizmet Planları Karşılaştırması',
                'api_title': 'API Entegrasyon Kılavuzu',
                'sdk_title': 'SDK Dokümantasyonu',
                'security_title': 'Güvenlik ve Uyumluluk',
                'support_title': 'Teknik Destek ve Kaynaklar',
                'onboarding_title': 'Hızlı Başlangıç Kılavuzu',
                'contact_title': 'İletişim Bilgileri'
            }
        }
        
    def create_header_footer(self, canvas, doc):
        """Create consistent header and footer"""
        canvas.saveState()
        
        # Header
        canvas.setFillColor(self.colors['primary'])
        canvas.rect(0, letter[1] - 1*inch, letter[0], 1*inch, fill=1)
        
        # PayCrypt logo/title in header
        canvas.setFillColor(white)
        canvas.setFont('Helvetica-Bold', 24)
        canvas.drawString(1*inch, letter[1] - 0.7*inch, 'PayCrypt Gateway')
        
        # Footer
        canvas.setFillColor(self.colors['light'])
        canvas.rect(0, 0, letter[0], 0.75*inch, fill=1)
        
        canvas.setFillColor(self.colors['secondary'])
        canvas.setFont('Helvetica', 9)
        canvas.drawString(1*inch, 0.3*inch, 
                         f'© {datetime.now().year} PayCrypt Gateway - Enterprise Crypto Payment Solution')
        
        # Page number
        canvas.drawRightString(letter[0] - 1*inch, 0.3*inch, 
                              f'Page {doc.page}')
        
        canvas.restoreState()
        
    def get_styles(self):
        """Define custom styles"""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=28,
            textColor=self.colors['primary'],
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=self.colors['primary'],
            spaceBefore=20,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='SubsectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.colors['secondary'],
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='CodeBlock',
            parent=styles['Code'],
            fontSize=10,
            fontName='Courier',
            backColor=self.colors['light'],
            borderPadding=10,
            spaceBefore=10,
            spaceAfter=10
        ))
        
        return styles
        
    def create_cover_page(self, story, styles):
        """Create professional cover page"""
        content = self.content[self.language]
        
        # Main title
        title = Paragraph(content['title'], styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Subtitle
        subtitle = Paragraph(content['subtitle'], styles['Title'])
        story.append(subtitle)
        story.append(Spacer(1, 1*inch))
        
        # Feature highlights box
        feature_data = [
            ['🚀', 'Enterprise-Grade Security'],
            ['⚡', 'Real-Time Processing'],
            ['🌍', 'Multi-Currency Support'],
            ['📊', 'Advanced Analytics'],
            ['🔧', 'Easy Integration'],
            ['📞', '24/7 Technical Support']
        ]
        
        feature_table = Table(feature_data, colWidths=[0.5*inch, 4*inch])
        feature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [white, self.colors['light']]),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['primary'])
        ]))
        
        story.append(feature_table)
        story.append(Spacer(1, 1*inch))
        
        # Contact info
        contact_info = Paragraph(f'''
        <para alignment="center">
        <b>Generated:</b> {datetime.now().strftime("%B %d, %Y")}<br/>
        <b>Version:</b> 1.0.0<br/>
        <b>Support:</b> support@paycrypt.online<br/>
        <b>Website:</b> https://paycrypt.online
        </para>
        ''', styles['Normal'])
        
        story.append(contact_info)
        story.append(PageBreak())
        
    def create_welcome_section(self, story, styles):
        """Create welcome section"""
        content = self.content[self.language]
        
        story.append(Paragraph(content['welcome_title'], styles['SectionTitle']))
        story.append(Paragraph(content['welcome_text'], styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
    def create_plans_comparison(self, story, styles):
        """Create service plans comparison table"""
        content = self.content[self.language]
        
        story.append(Paragraph(content['plans_title'], styles['SectionTitle']))
        
        # Plans comparison data
        plans_data = [
            ['Feature', 'Starter', 'Professional', 'Enterprise'],
            ['Monthly Transactions', '1,000', '10,000', 'Unlimited'],
            ['Commission Rate', '2.5%', '2.0%', 'Custom'],
            ['API Calls/Hour', '1,000', '10,000', 'Unlimited'],
            ['Supported Currencies', '5', '15', 'All Available'],
            ['Webhook Support', '✓', '✓', '✓'],
            ['Analytics Dashboard', '✓', '✓', '✓'],
            ['Priority Support', '✗', '✓', '✓'],
            ['Custom Integration', '✗', '✗', '✓'],
            ['SLA Guarantee', '99%', '99.5%', '99.9%']
        ]
        
        plans_table = Table(plans_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        plans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, self.colors['light']]),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['secondary'])
        ]))
        
        story.append(plans_table)
        story.append(Spacer(1, 0.3*inch))
        
    def create_api_guide(self, story, styles):
        """Create API integration guide"""
        story.append(Paragraph('API Integration Guide', styles['SectionTitle']))
        
        # Base URL info
        story.append(Paragraph('Base URL Configuration', styles['SubsectionTitle']))
        story.append(Paragraph('''
        Configure your integration to use the PayCrypt Gateway API endpoints:
        ''', styles['Normal']))
        
        api_config = '''
Production: https://api.paycrypt.online/v1
Sandbox: https://sandbox-api.paycrypt.online/v1
        '''
        story.append(Paragraph(api_config, styles['CodeBlock']))
        
        # Authentication
        story.append(Paragraph('Authentication', styles['SubsectionTitle']))
        auth_example = '''
import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json',
    'X-HMAC-Signature': hmac_signature
}

response = requests.post('https://api.paycrypt.online/v1/payments', 
                        headers=headers, json=payment_data)
        '''
        story.append(Paragraph(auth_example, styles['CodeBlock']))
        
        # Core endpoints
        story.append(Paragraph('Core API Endpoints', styles['SubsectionTitle']))
        
        endpoints_data = [
            ['Endpoint', 'Method', 'Description'],
            ['/payments', 'POST', 'Create new payment'],
            ['/payments/{id}', 'GET', 'Get payment status'],
            ['/payments/{id}/confirm', 'POST', 'Confirm payment'],
            ['/wallets', 'GET', 'List available wallets'],
            ['/rates', 'GET', 'Get current exchange rates'],
            ['/webhooks', 'POST', 'Register webhook URL']
        ]
        
        endpoints_table = Table(endpoints_data, colWidths=[2.5*inch, 1*inch, 3.5*inch])
        endpoints_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, self.colors['light']]),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['secondary'])
        ]))
        
        story.append(endpoints_table)
        story.append(Spacer(1, 0.3*inch))
        
    def create_sdk_section(self, story, styles):
        """Create SDK documentation section"""
        story.append(Paragraph('SDK Documentation', styles['SectionTitle']))
        
        # Python SDK
        story.append(Paragraph('Python SDK', styles['SubsectionTitle']))
        python_example = '''
from paycrypt_sdk import PayCryptClient

# Initialize client
client = PayCryptClient(
    api_key="your_api_key",
    secret_key="your_secret_key",
    environment="production"  # or "sandbox"
)

# Create payment
payment = client.payments.create({
    "amount": 100.00,
    "currency": "USD",
    "crypto_currency": "BTC",
    "callback_url": "https://yoursite.com/webhook",
    "return_url": "https://yoursite.com/success"
})

print(f"Payment ID: {payment.id}")
print(f"Payment URL: {payment.payment_url}")
        '''
        story.append(Paragraph(python_example, styles['CodeBlock']))
        
        # JavaScript SDK
        story.append(Paragraph('JavaScript SDK', styles['SubsectionTitle']))
        js_example = '''
import PayCrypt from 'paycrypt-js-sdk';

const paycrypt = new PayCrypt({
  apiKey: 'your_api_key',
  secretKey: 'your_secret_key',
  environment: 'production'
});

// Create payment
const payment = await paycrypt.payments.create({
  amount: 100.00,
  currency: 'USD',
  cryptoCurrency: 'BTC',
  callbackUrl: 'https://yoursite.com/webhook',
  returnUrl: 'https://yoursite.com/success'
});

console.log('Payment ID:', payment.id);
        '''
        story.append(Paragraph(js_example, styles['CodeBlock']))
        
    def create_security_section(self, story, styles):
        """Create security and compliance section"""
        story.append(Paragraph('Security & Compliance', styles['SectionTitle']))
        
        security_features = [
            ['Security Feature', 'Implementation'],
            ['HMAC Verification', 'SHA-256 signature validation for all requests'],
            ['API Rate Limiting', 'Configurable limits to prevent abuse'],
            ['SSL/TLS Encryption', 'End-to-end encryption for all communications'],
            ['Webhook Security', 'Signed webhooks with timestamp validation'],
            ['Access Control', 'Role-based permissions and IP whitelisting'],
            ['Audit Logging', 'Comprehensive logs for all transactions'],
            ['Compliance', 'SOC 2 Type II, PCI DSS compliant infrastructure']
        ]
        
        security_table = Table(security_features, colWidths=[2.5*inch, 4.5*inch])
        security_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['success']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, self.colors['light']]),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['secondary'])
        ]))
        
        story.append(security_table)
        story.append(Spacer(1, 0.3*inch))
        
    def create_onboarding_checklist(self, story, styles):
        """Create quick start checklist"""
        story.append(Paragraph('Quick Start Onboarding Checklist', styles['SectionTitle']))
        
        checklist_items = [
            '□ Account Setup & Verification',
            '□ API Key Generation',
            '□ Webhook URL Configuration',
            '□ SDK Installation & Testing',
            '□ Sandbox Environment Testing',
            '□ Production Deployment',
            '□ Monitoring & Analytics Setup',
            '□ Support Channel Configuration'
        ]
        
        for item in checklist_items:
            story.append(Paragraph(item, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
        story.append(Spacer(1, 0.3*inch))
        
    def create_support_section(self, story, styles):
        """Create support and resources section"""
        story.append(Paragraph('Technical Support & Resources', styles['SectionTitle']))
        
        support_info = '''
        <b>Technical Support:</b><br/>
        Email: support@paycrypt.online<br/>
        Response Time: &lt; 4 hours (Enterprise), &lt; 24 hours (Standard)<br/><br/>
        
        <b>Developer Resources:</b><br/>
        API Documentation: https://docs.paycrypt.online<br/>
        Status Page: https://status.paycrypt.online<br/>
        Developer Portal: https://developers.paycrypt.online<br/><br/>
        
        <b>Integration Support:</b><br/>
        Slack Community: paycrypt-developers.slack.com<br/>
        GitHub: https://github.com/paycrypt<br/>
        Sample Code: https://github.com/paycrypt/examples
        '''
        
        story.append(Paragraph(support_info, styles['Normal']))
        
    def generate_pdf(self, filename=None):
        """Generate the complete PDF"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"PayCrypt_Launch_Kit_{self.language.upper()}_{timestamp}.pdf"
            
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=1*inch, leftMargin=1*inch,
                              topMargin=1.2*inch, bottomMargin=1*inch)
        
        # Get styles
        styles = self.get_styles()
        
        # Build story
        story = []
        
        # Add all sections
        self.create_cover_page(story, styles)
        self.create_welcome_section(story, styles)
        self.create_plans_comparison(story, styles)
        
        story.append(PageBreak())
        self.create_api_guide(story, styles)
        
        story.append(PageBreak())
        self.create_sdk_section(story, styles)
        
        story.append(PageBreak())
        self.create_security_section(story, styles)
        self.create_onboarding_checklist(story, styles)
        self.create_support_section(story, styles)
        
        # Build PDF with custom header/footer
        doc.build(story, onFirstPage=self.create_header_footer,
                 onLaterPages=self.create_header_footer)
        
        print(f"✅ Launch Kit PDF generated: {filename}")
        return filename

def main():
    """Generate launch kits in multiple languages"""
    languages = ['en', 'tr']
    
    print("🚀 Generating PayCrypt Launch Kit PDFs...")
    
    generated_files = []
    for lang in languages:
        try:
            generator = PayCryptLaunchKitPDF(language=lang)
            filename = generator.generate_pdf()
            generated_files.append(filename)
        except Exception as e:
            print(f"❌ Error generating {lang.upper()} PDF: {str(e)}")
            
    print(f"\n📚 Generated {len(generated_files)} launch kit PDFs:")
    for file in generated_files:
        print(f"  - {file}")
        
    print("\n🎉 Launch Kit generation complete!")

if __name__ == '__main__':
    main()
