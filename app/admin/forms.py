from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.utils import ORDER_STATUSES


class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Save category")


class ServiceForm(FlaskForm):
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired(), Length(max=160)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1000)])
    price = IntegerField("Price", validators=[DataRequired(), NumberRange(min=0)])
    is_active = BooleanField("Active")
    submit = SubmitField("Save service")


class UserRoleForm(FlaskForm):
    role = SelectField(
        "Role",
        choices=[
            ("customer", "Customer"),
            ("service_officer", "Service Officer"),
            ("accountant", "Accountant"),
            ("admin", "Admin"),
            ("super_admin", "Super Admin"),
        ],
    )
    is_active = BooleanField("Active")
    submit = SubmitField("Update user")


class OrderStatusForm(FlaskForm):
    status = SelectField("Status", choices=[(status, status.replace("_", " ").title()) for status in ORDER_STATUSES])
    admin_notes = TextAreaField("Admin notes", validators=[Optional(), Length(max=1500)])
    result_file = FileField("Completed file", validators=[FileAllowed(["pdf", "docx", "jpg", "jpeg", "png", "zip"])])
    submit = SubmitField("Update order")
