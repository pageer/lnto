from flask_wtf import FlaskForm
from wtforms import PasswordField, validators

class ChangePassword(FlaskForm):
    new_password = PasswordField("New password", [
        validators.DataRequired(),
        validators.Length(min=3)
    ])
    confirm = PasswordField("Confirm", [
        validators.DataRequired(),
        validators.Length(min=3)
    ])

    def validate_confirm(self, field):
        match = self.new_password.data == field.data
        if not match:
            raise validators.ValidationError("Passwords do not match")
