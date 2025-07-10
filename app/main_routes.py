from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, session, flash, send_from_directory
from app import db
from app.models import Payment
from app.models.client_package import ClientPackage, ClientType, PackageStatus, REVISED_FLAT_RATE_PACKAGES
from app.models.client import Client
from app.models.user import User
from app.forms.client_forms import ClientRegistrationForm
from app.utils import generate_address, generate_order_id, create_qr
import logging
import os

logger = logging.getLogger(__name__)

# Create main blueprint
main = Blueprint('main', __name__, url_prefix='/')

@main.route('/favicon.ico')
def favicon():
    """Serve favicon from root URL"""
    return send_from_directory(
        os.path.join(current_app.root_path, 'static', 'img'), 
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@main.route('/')
def landing():
    """Landing page with single package model"""
    # Get prices from REVISED_FLAT_RATE_PACKAGES
    starter = REVISED_FLAT_RATE_PACKAGES['starter_flat_rate']
    business = REVISED_FLAT_RATE_PACKAGES['business_flat_rate']
    enterprise = REVISED_FLAT_RATE_PACKAGES['enterprise_flat_rate']

    def annual_price(monthly):
        return monthly * 12 * 0.9  # 10% discount

    return render_template(
        'landing.html',
        starter_price_monthly=f"${int(starter['monthly_price']):,}",
        starter_price_annual=f"${int(annual_price(starter['monthly_price'])):,}",
        business_price_monthly=f"${int(business['monthly_price']):,}",
        business_price_annual=f"${int(annual_price(business['monthly_price'])):,}",
        enterprise_price_monthly=f"${int(enterprise['monthly_price']):,}",
        enterprise_price_annual=f"${int(annual_price(enterprise['monthly_price'])):,}"
    )

@main.route('/pricing')
def pricing():
    """Pricing page with package selection"""
    from app.models.client_package import ClientPackage, ClientType, COMMISSION_BASED_PACKAGES
    # Query DB for flat-rate packages so pkg.slug is the model property
    packages_flatrate = {pkg.slug: pkg for pkg in ClientPackage.query.filter_by(client_type=ClientType.FLAT_RATE).all()}
    packages_commission = COMMISSION_BASED_PACKAGES
    return render_template(
        'pricing.html',
        packages_flatrate=packages_flatrate,
        packages_commission=packages_commission
    )

@main.route('/terms')
def terms():
    """Terms of Service page"""
    return render_template('legal/terms.html')

@main.route('/privacy')
def privacy():
    """Privacy Policy page"""
    return render_template('legal/privacy.html')

@main.route('/api/packages')
def get_packages():
    """API endpoint to get available packages"""
    try:
        commission_packages = ClientPackage.query.filter(
            ClientPackage.client_type == ClientType.COMMISSION,
            ClientPackage.status == PackageStatus.ACTIVE
        ).order_by(ClientPackage.sort_order).all()
        
        flat_rate_packages = ClientPackage.query.filter(
            ClientPackage.client_type == ClientType.FLAT_RATE,
            ClientPackage.status == PackageStatus.ACTIVE
        ).order_by(ClientPackage.sort_order).all()
        
        def package_to_dict(package):
            return {
                'id': package.id,
                'name': package.name,
                'description': package.description,
                'client_type': package.client_type.value,
                'price': float(package.monthly_price) if package.monthly_price else None,
                'commission_rate': float(package.commission_rate * 100) if package.commission_rate else None,
                'is_popular': package.is_popular,
                'features': [f.feature.name for f in package.package_features if f.is_included],
                'max_transactions': package.max_transactions_per_month,
                'max_api_calls': package.max_api_calls_per_month,
                'max_wallets': package.max_wallets
            }
        
        return jsonify({
            'commission': [package_to_dict(p) for p in commission_packages],
            'flat_rate': [package_to_dict(p) for p in flat_rate_packages]
        })
    
    except Exception as e:
        logger.error(f"Error fetching packages: {e}")
        return jsonify({'error': 'Failed to fetch packages'}), 500

@main.route('/register')
def register():
    """Registration page with package pre-selection"""
    package_param = request.args.get('package')
    selected_package = None
    from app.models.client_package import ClientPackage, ClientType
    if package_param:
        try:
            # Try as integer ID first
            selected_package = ClientPackage.query.get(int(package_param))
        except (ValueError, TypeError):
            # Try as slug (for flat-rate plans)
            selected_package = ClientPackage.query.filter(
                ClientPackage.client_type == ClientType.FLAT_RATE
            ).all()
            # Find the package whose .slug property matches the param
            selected_package = next((p for p in selected_package if p.slug == package_param), None)
            if not selected_package:
                flash('Invalid package selection', 'error')
    form = ClientRegistrationForm()
    if selected_package:
        form.package_id.data = str(selected_package.id)
    return render_template('auth/register.html', 
                     form=form, 
                     selected_package=selected_package)

@main.route('/register', methods=['POST'])
def register_post():
    """Handle registration form submission"""
    form = ClientRegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Get selected package
            package = None
            if form.package_id.data:
                package = ClientPackage.query.get(int(form.package_id.data))
                if not package:
                    flash('Invalid package selection', 'error')
                    return render_template('auth/register.html', form=form)
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Email already registered', 'error')
                return render_template('auth/register.html', form=form, selected_package=package)
            
            existing_client = Client.query.filter_by(email=form.email.data).first()
            if existing_client:
                flash('Email already registered', 'error')
                return render_template('auth/register.html', form=form, selected_package=package)
            
            # Create user account
            from werkzeug.security import generate_password_hash
            user = User(
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data),
                role='client',
                is_active=True,
                is_verified=False  # Require email verification
            )
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Create client profile
            client = Client(
                user_id=user.id,
                company_name=form.company_name.data,
                contact_person=form.contact_person.data,
                email=form.email.data,
                contact_email=form.contact_email.data or form.email.data,
                phone=form.phone.data,
                contact_phone=form.contact_phone.data,
                address=form.address.data,
                city=form.city.data,
                country=form.country.data,
                postal_code=form.postal_code.data,
                tax_id=form.tax_id.data,
                vat_number=form.vat_number.data,
                registration_number=form.registration_number.data,
                website=form.website.data,
                package_id=package.id if package else None,
                is_active=True,
                is_verified=False
            )
            db.session.add(client)
            
            # Link user to client
            user.client = client
            
            db.session.commit()
            
            # Log the user in (will need to import login_user when Flask-Login is available)
            flash(f'Registration successful! Welcome to {package.name if package else "our platform"}!', 'success')
            
            # For now, redirect to login page since Flask-Login may not be configured
            return redirect(url_for('auth.client_login'))
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
            
    else:
        # Form validation failed
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    # Re-render form with errors
    selected_package = None
    if form.package_id.data:
        try:
            selected_package = ClientPackage.query.get(int(form.package_id.data))
        except (ValueError, TypeError):
            pass
    
    return render_template('auth/register.html', 
                     form=form, 
                     selected_package=selected_package)

@main.route('/initiate-payment', methods=['POST'])
def initiate_payment():
    # Note: Add authentication check here when implementing
    data = request.get_json()
    amount = data.get('amount')
    currency = data.get('currency', 'USD')
    
    if not amount:
        return jsonify({'error': 'Amount is required'}), 400
    
    try:
        # Create payment record
        payment = Payment(
            amount=amount,
            currency=currency,
            status='pending',
            order_id=generate_order_id(),
            payment_address=generate_address()
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Create QR code for payment
        qr_code = create_qr(payment.payment_address)
        
        return jsonify({
            'payment_id': payment.id,
            'order_id': payment.order_id,
            'amount': float(amount),
            'currency': currency,
            'payment_address': payment.payment_address,
            'qr_code': qr_code
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error initiating payment: {str(e)}')
        return jsonify({'error': 'Failed to initiate payment'}), 500

@main.route('/reset-db', methods=['POST'])
def reset_db():
    # Note: Add proper admin authentication here
    if not current_app.config.get('DEBUG'):
        return jsonify({'error': 'This endpoint is only available in debug mode'}), 403
    
    try:
        db.drop_all()
        db.create_all()
        return jsonify({'message': 'Database reset successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error resetting database: {str(e)}')
        return jsonify({'error': 'Failed to reset database'}), 500

@main.route('/set-language/<language>')
def set_language(language=None):
    """Set the user's preferred language"""
    from app.utils.i18n import set_language as set_user_language, get_supported_languages
    
    if language and set_user_language(language):
        current_app.logger.info(f"Language set to: {language}")
    else:
        current_app.logger.warning(f"Invalid language code: {language}")
    
    # Redirect back to the previous page or dashboard
    return redirect(request.referrer or url_for('main.home'))

@main.route('/api/languages')
def api_languages():
    """API endpoint to get supported languages"""
    from app.utils.i18n import get_supported_languages, get_current_language
    
    return jsonify({
        'current': get_current_language(),
        'supported': get_supported_languages()
    })
