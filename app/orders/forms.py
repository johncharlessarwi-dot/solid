from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

ALLOWED = ["pdf", "docx", "jpg", "jpeg", "png", "zip"]


class OrderForm(FlaskForm):
    service_id = SelectField("Service", coerce=int, validators=[DataRequired()])
    notes = TextAreaField("Instructions", validators=[Optional(), Length(max=1500)])
    documents = MultipleFileField("Documents", validators=[FileAllowed(ALLOWED, "Allowed: PDF, DOCX, JPG, PNG, ZIP")])
    submit = SubmitField("Submit order")
