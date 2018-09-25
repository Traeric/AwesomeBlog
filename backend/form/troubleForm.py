from django.forms import forms, fields, widgets


class TroubleForm(forms.Form):
    trouble_id = fields.IntegerField(required=False, widget=widgets.TextInput(attrs={"type": 'hidden'}))
    title = fields.CharField(max_length=64, required=True, strip=True,
                             widget=widgets.TextInput(attrs={"class": "form-control"}))
    detail = fields.CharField(
        required=True,
        strip=True,
        widget=widgets.Textarea(attrs={"id": "detail", "class": "form-control"})
    )






