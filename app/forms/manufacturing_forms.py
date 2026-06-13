from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional


class ManufacturingOrderForm(FlaskForm):
    product_id = SelectField("Product", coerce=int, validators=[DataRequired()])
    quantity = FloatField("Quantity", validators=[DataRequired()])
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Create MO")


class WorkCenterForm(FlaskForm):
    name = StringField("Work Center Name", validators=[DataRequired()])
    code = StringField("Code")
    description = TextAreaField("Description")
    department = StringField("Department")
    capacity_per_shift = FloatField("Capacity per Shift", default=1.0)
    cost_per_hour = FloatField("Cost per Hour", default=0.0)
    submit = SubmitField("Save")
