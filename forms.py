# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class FoodIntakeForm(FlaskForm):
    meal_type = StringField('Meal', validators=[DataRequired()])
    intake_level = SelectField('Food Intake', choices=[('25%', '25%'), ('50%', '50%'), ('75%', '75%'), ('100%', '100%'), ('Ensure', 'Ensure'), ('Other', 'Other')], validators=[DataRequired()])
    notes = TextAreaField('Notes (for Other)', render_kw={'rows': 4})
    submit = SubmitField('Submit')

class LiquidIntakeForm(FlaskForm):
    liquid = StringField('Liquid Type', validators=[DataRequired()])
    amount = StringField('Amount', validators=[DataRequired()])
    submit = SubmitField('Submit')

class BowelMovementForm(FlaskForm):
    size = SelectField('Size', choices=[('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large')], validators=[DataRequired()])
    consistency = SelectField('Consistency', choices=[('Soft', 'Soft'), ('Medium', 'Medium'), ('Hard', 'Hard')], validators=[DataRequired()])
    submit = SubmitField('Submit')

class UrineOutputForm(FlaskForm):
    output = SelectField('Urine Output', choices=[('Yes', 'Yes'), ('No', 'No')], validators=[DataRequired()])
    submit = SubmitField('Submit')