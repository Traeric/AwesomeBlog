from django.core.exceptions import ValidationError
from django.forms import forms, fields, widgets
from repository import models


# 登陆表单
class LoginForm(forms.Form):
    username = fields.CharField(
        max_length=16,
        min_length=1,
        required=True,
        strip=True,
        widget=widgets.TextInput(attrs={"placeholder": "用户名"}))
    pwd = fields.CharField(
        required=True,
        max_length=32,
        min_length=6,
        strip=True,
        widget=widgets.PasswordInput(attrs={"placeholder": "密码"}))
    confirm_code = fields.CharField(
        required=True,
        max_length=4,
        min_length=4,
        strip=True,
        widget=widgets.TextInput(attrs={"placeholder": "验证码", "style": "width: 50%; float: left;"}))
    remenber_me = fields.CharField(
        required=False,
        widget=widgets.CheckboxInput(attrs={"id": "brand1"})
    )

    def __init__(self, right_code="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.right_code = right_code

    def clean(self):
        try:
            username = self.cleaned_data["username"]
            pwd = self.cleaned_data["pwd"]
            if not models.User.objects.filter(username=username, pwd=pwd).exists():
                raise ValidationError("密码输入有误")
            return self.cleaned_data
        except KeyError:
            return self.cleaned_data

    def clean_username(self):
        # 验证用户名是否输入正确
        username = self.cleaned_data["username"]
        if not models.User.objects.filter(username=username).exists():
            # 如果不存在,抛异常
            raise ValidationError("用户名有误")
        return username

    def clean_confirm_code(self):
        # 判断验证码是否输入正确
        code = self.cleaned_data['confirm_code']
        if not self.right_code == code:
            raise ValidationError("验证码有误")
        return code


