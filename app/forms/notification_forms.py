from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField
from app.models.notification import NotificationType, NotificationEvent

class NotificationPreferenceForm(FlaskForm):
    """Form for managing notification preferences"""
    
    # Hidden field to store user ID
    user_id = HiddenField()
    
    # Generate fields dynamically based on notification types and events
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Create fields for each combination of notification type and event
        for nt in NotificationType:
            for et in NotificationEvent:
                field_name = f'pref_{nt.value}_{et.value}'
                setattr(self, field_name, BooleanField(
                    f'{nt.name.title()} - {et.name.replace("_", " ").title()}'
                ))

    def get_preferences(self):
        """Get the preferences from the form data"""
        preferences = []
        for nt in NotificationType:
            for et in NotificationEvent:
                field_name = f'pref_{nt.value}_{et.value}'
                if hasattr(self, field_name):
                    preferences.append({
                        'type': nt.value,
                        'event': et.value,
                        'enabled': getattr(self, field_name).data
                    })
        return preferences
