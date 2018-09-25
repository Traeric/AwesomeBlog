from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import forms, widgets
from django.forms import fields
from repository import models
# 注册的Form


class RegisterForm(forms.Form):
    username = fields.CharField(
        max_length=16,
        min_length=1,
        required=True,
        strip=True,
        validators=[
            RegexValidator(r'^[a-zA-Z\u4e00-\u9fa5]+$', '用户名不能有特殊字符或数字'),
        ],
        widget=widgets.TextInput(attrs={"placeholder": "用户名"}))
    email = fields.CharField(
        required=True,
        strip=True,
        validators=[
            RegexValidator(r'^\d{5,12}@[qQ][qQ]\.(com|cn)$', '只能是QQ邮箱'),
        ],
        widget=widgets.TextInput(attrs={"placeholder": "邮箱"}))
    pwd = fields.CharField(
        required=True,
        max_length=32,
        min_length=6,
        strip=True,
        widget=widgets.PasswordInput(attrs={"placeholder": "密码"}),
        validators=[
            RegexValidator(r"([0-9]+.+[a-zA-Z]+|[a-zA-Z]+.+[0-9]+)", "密码必须包含数字跟字母"),
        ])
    re_password = fields.CharField(
        required=True,
        max_length=32,
        min_length=6,
        strip=True,
        widget=widgets.PasswordInput(attrs={"placeholder": "确认密码"}))
    confirm_code = fields.CharField(required=True, max_length=4, min_length=4, strip=True,
                                    widget=widgets.TextInput(attrs={"placeholder": "验证码", "style": "width: 50%; float: left;"}))

    def __init__(self, right_code="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.right_code = right_code

    def clean_confirm_code(self):
        # 判断验证码是否输入正确
        code = self.cleaned_data['confirm_code']
        if not self.right_code == code:
            raise ValidationError("验证码有误")
        return code

    def clean_username(self):
        # 判断用户名是否有重复
        username = self.cleaned_data["username"]
        if models.User.objects.filter(username=username).exists():
            # 如果存在抛出异常
            raise ValidationError("该用户名已存在")
        return username

    def clean_email(self):
        # 判断邮箱是否重复
        email = self.cleaned_data['email']
        if models.User.objects.filter(email=email).exists():
            raise ValidationError("该邮箱已注册")
        return email

    def clean(self):
        try:
            # 在这里面判断两次输入的密码是否一致
            password = self.cleaned_data['pwd']
            re_password = self.cleaned_data['re_password']
            if not password == re_password:
                # 两次输入的密码不一致
                raise ValidationError("两次密码输入不一致")
            return self.cleaned_data
        except KeyError:
            return self.cleaned_data


