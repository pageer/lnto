# pylint: disable=too-few-public-methods, import-error
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, \
                    HiddenField, validators

class AddUser(FlaskForm):
    username = StringField(
        "Username",
        [validators.DataRequired("You must give a username")],
        filters=[lambda x: x.strip()]
    )
    password = PasswordField(
        "Password",
        [
            validators.DataRequired("You must give a password"),
            validators.Length(min=3)
        ],
        filters=[lambda x: x.strip()]
    )
    confirm = PasswordField("Confirm", [
        validators.DataRequired(),
        validators.Length(min=3)
    ])

    def validate_confirm(self, field):
        match = self.password.data == field.data
        if not match:
            raise validators.ValidationError('Passwords do not match')


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


class AddLink(FlaskForm):
    name = StringField(
        "Title",
        [validators.DataRequired("Title is required")],
        render_kw={'placeholder': "Link description (auto-fetched)"}
    )
    shortname = StringField(
        "Short name",
        render_kw={
            'placeholder': "(Optional) A unique short name to access the URL",
        }
    )
    url = StringField(
        "Link",
        [validators.DataRequired("URL is required")],
        render_kw={
            'placeholder': "Type or paste URL",
            'autofocus': True
        }
    )
    description = TextAreaField(
        "Description",
        render_kw={
            'placeholder': "Link description (auto-fetched)",
            'rows': 4,
            'cols': 40
        }
    )
    tags = StringField(
        "Tags",
        filters=[lambda x: x.strip()],
        render_kw={'placeholder': "Comma-separated list of tags"}
    )
    is_public = BooleanField("Is public")
    referer = HiddenField()
    redirect_to_target = HiddenField(default="0")
