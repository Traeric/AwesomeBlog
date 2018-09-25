from django.forms import forms, fields, widgets


class HandleTroubleForm(forms.Form):
    trouble_id = fields.IntegerField(required=False, widget=widgets.TextInput(attrs={"type": 'hidden'}))
    title = fields.CharField(max_length=64,
                             widget=widgets.TextInput(attrs={"class": "form-control"}))
    detail = fields.CharField(
        widget=widgets.Textarea(attrs={"class": "form-control"})
    )
    solve_plan = fields.CharField(
        required=True,
        strip=True,
        widget=widgets.Textarea(attrs={"id": "solve_plan"})
    )





