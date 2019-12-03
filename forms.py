from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class SearchForm(FlaskForm):
    searchInput = StringField('SearchInput',
                              validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Go!')


class ClassifierForm(FlaskForm):
    classifierInput = StringField('ClassifierInput',
                                  validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Go!')
