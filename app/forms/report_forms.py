from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Optional
from app.models.report import ReportType, ReportFilterType

class ReportForm(FlaskForm):
    """Form for creating and configuring reports"""
    name = StringField('Report Name', validators=[DataRequired()])
    description = StringField('Description')
    report_type = SelectField('Report Type', choices=[(rt.value, rt.name.replace('_', ' ').title()) 
                                                   for rt in ReportType],
                            validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add dynamic fields based on report type
        if 'report_type' in kwargs:
            self._add_dynamic_fields(kwargs['report_type'])
    
    def _add_dynamic_fields(self, report_type):
        """Add dynamic fields based on report type"""
        if report_type == ReportType.CLIENT_ANALYSIS.value:
            self.client_group = SelectField('Client Group', 
                                          choices=[('all', 'All Clients'),
                                                  ('active', 'Active Clients'),
                                                  ('inactive', 'Inactive Clients')])
        elif report_type == ReportType.PAYMENT_METHODS.value:
            self.currency = SelectField('Currency', 
                                      choices=[('all', 'All Currencies'),
                                              ('USD', 'USD'),
                                              ('EUR', 'EUR'),
                                              ('GBP', 'GBP')])
        elif report_type == ReportType.OVERDUE_PAYMENTS.value:
            self.max_age = IntegerField('Maximum Age (days)', 
                                      validators=[Optional()],
                                      default=90)
            self.include_details = BooleanField('Include Payment Details')

    def get_filters(self):
        """Get the filters from the form data"""
        filters = {
            'start_date': self.start_date.data,
            'end_date': self.end_date.data
        }
        
        if hasattr(self, 'client_group'):
            filters['client_group'] = self.client_group.data
        if hasattr(self, 'currency'):
            filters['currency'] = self.currency.data
        if hasattr(self, 'max_age'):
            filters['max_age'] = self.max_age.data
        if hasattr(self, 'include_details'):
            filters['include_details'] = self.include_details.data
        
        return filters
