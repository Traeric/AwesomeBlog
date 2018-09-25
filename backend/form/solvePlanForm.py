from django.forms import forms, fields, widgets
from repository import models


class SolvePlanForm(forms.Form):
    trouble_id = fields.IntegerField(required=False, widget=widgets.TextInput(attrs={"type": 'hidden'}))
    evaluate = fields.CharField(
        required=True,
        widget=widgets.Select(choices=models.Trouble.evaluate_choices)
    )



