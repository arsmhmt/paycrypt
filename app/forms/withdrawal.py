from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Optional
from decimal import Decimal

class WithdrawalForm(FlaskForm):
    coin = SelectField(
        'Cryptocurrency',
        choices=[
            ('USDT', 'Tether (USDT)'),
            ('BTC', 'Bitcoin (BTC)'),
            ('ETH', 'Ethereum (ETH)'),
            ('BNB', 'Binance Coin (BNB)'),
            ('ADA', 'Cardano (ADA)'),
            ('XRP', 'Ripple (XRP)')
        ],
        validators=[DataRequired()],
        default='USDT'
    )
    
    blockchain = SelectField(
        'Blockchain Network',
        choices=[
            ('ERC20', 'Ethereum (ERC-20)'),
            ('TRC20', 'Tron (TRC-20)'),
            ('BEP20', 'BNB Smart Chain (BEP-20)'),
            ('BTC', 'Bitcoin Network'),
            ('ETH', 'Ethereum Native'),
            ('BNB', 'BNB Chain'),
            ('ADA', 'Cardano Network'),
            ('XRP', 'XRP Ledger')
        ],
        validators=[DataRequired()],
        default='TRC20'
    )
    
    amount = DecimalField(
        'Withdrawal Amount',
        validators=[
            DataRequired(message='Please enter an amount'),
            NumberRange(
                min=0.01,
                message='Minimum withdrawal amount is 0.01'
            )
        ],
        places=8,
        render_kw={
            'placeholder': '0.00',
            'step': '0.01',
            'class': 'form-control',
            'id': 'withdrawalAmount'
        }
    )
    
    address = StringField(
        'Wallet Address',
        validators=[
            DataRequired(message='Please enter a wallet address')
        ],
        render_kw={
            'placeholder': 'Enter your wallet address',
            'class': 'form-control',
            'id': 'walletAddress'
        }
    )
    
    memo = StringField(
        'Memo/Tag (Optional)',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Required for some exchanges (XRP, XLM, etc.)',
            'class': 'form-control'
        }
    )
    
    submit = SubmitField('Request Withdrawal', render_kw={'class': 'btn btn-primary btn-lg w-100'})
    
    def validate_amount(self, field):
        """Validate withdrawal amount"""
        if field.data <= 0:
            raise ValidationError('Withdrawal amount must be positive')
        
        # Additional validation based on coin
        coin = self.coin.data.upper()
        min_amounts = {
            'USDT': 10.0,
            'BTC': 0.001,
            'ETH': 0.01,
            'BNB': 0.1,
            'ADA': 10.0,
            'XRP': 20.0
        }
        
        min_amount = min_amounts.get(coin, 0.01)
        if field.data < min_amount:
            raise ValidationError(f'Minimum withdrawal amount for {coin} is {min_amount}')
    
    def validate_address(self, field):
        """Enhanced crypto address validation with blockchain support"""
        address = field.data.strip()
        coin = self.coin.data.upper()
        blockchain = self.blockchain.data.upper()
        
        # Basic length and format validation
        if len(address) < 10:
            raise ValidationError('Wallet address is too short')
        
        # Blockchain-specific validation
        if blockchain == 'ERC20' or blockchain == 'ETH':
            # Ethereum address validation
            if not (address.startswith('0x') and len(address) == 42):
                raise ValidationError('Invalid Ethereum address format (must start with 0x and be 42 characters)')
        elif blockchain == 'TRC20':
            # Tron address validation
            if not (address.startswith('T') and len(address) == 34):
                raise ValidationError('Invalid Tron address format (must start with T and be 34 characters)')
        elif blockchain == 'BEP20' or blockchain == 'BNB':
            # Binance Smart Chain address validation
            if not (address.startswith(('0x', 'bnb')) and len(address) in [42, 43]):
                raise ValidationError('Invalid BNB address format')
        elif blockchain == 'BTC':
            # Bitcoin address validation
            if not (address.startswith(('1', '3', 'bc1')) and 26 <= len(address) <= 90):
                raise ValidationError('Invalid Bitcoin address format')
        elif blockchain == 'ADA':
            # Cardano address validation
            if not (address.startswith('addr') and len(address) > 50):
                raise ValidationError('Invalid Cardano address format')
        elif blockchain == 'XRP':
            # XRP address validation
            if not (address.startswith('r') and 25 <= len(address) <= 35):
                raise ValidationError('Invalid XRP address format')
    
    def validate_blockchain_coin_compatibility(self):
        """Validate that the selected blockchain is compatible with the coin"""
        coin = self.coin.data.upper()
        blockchain = self.blockchain.data.upper()
        
        # Define compatible blockchain-coin pairs
        compatibility = {
            'USDT': ['ERC20', 'TRC20', 'BEP20'],
            'BTC': ['BTC'],
            'ETH': ['ETH', 'ERC20'],
            'BNB': ['BNB', 'BEP20'],
            'ADA': ['ADA'],
            'XRP': ['XRP']
        }
        
        if coin in compatibility and blockchain not in compatibility[coin]:
            valid_blockchains = ', '.join(compatibility[coin])
            raise ValidationError(f'{coin} is only available on: {valid_blockchains}')

class AdminWithdrawalActionForm(FlaskForm):
    """Form for admin actions on withdrawal requests"""
    action = SelectField(
        'Action',
        choices=[
            ('approve', 'Approve'),
            ('reject', 'Reject'),
            ('complete', 'Mark as Completed'),
            ('cancel', 'Cancel')
        ],
        validators=[DataRequired()]
    )
    
    admin_note = TextAreaField(
        'Admin Note',
        validators=[Optional()],
        render_kw={
            'rows': 3,
            'placeholder': 'Add a note about this action (optional for approval, required for rejection)'
        }
    )
    
    tx_hash = StringField(
        'Transaction Hash',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Enter transaction hash if completed (optional)'
        }
    )
    
    submit = SubmitField('Process Action')
