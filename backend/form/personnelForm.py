from django.core.validators import RegexValidator
from django.forms import forms, fields, widgets
from repository import models


class PersonnelForm(forms.Form):
    user_name = fields.CharField(
        max_length=16,
        required=True,
        strip=True,
        validators=[
            RegexValidator(r'^[a-zA-Z\u4e00-\u9fa5]+$', '用户名不能有特殊字符或数字'),
        ],
        widget=widgets.TextInput(attrs={"placeholder": "用户名"})
    )
    email = fields.CharField(
        max_length=32,
        required=True,
        strip=True,
        validators=[
            RegexValidator(r'^\d{5,12}@[Qq][Qq]\.(com|cn)$', '只能是QQ邮箱'),
        ],
        widget=widgets.TextInput(attrs={"placeholder": "邮箱"})
    )
    blog_title = fields.CharField(
        max_length=16,
        required=True,
        strip=True,
        widget=widgets.TextInput(attrs={"placeholder": "博客标题"})
    )
    blog_surfix = fields.CharField(
        max_length=32,
        required=True,
        strip=True,
        validators=[
            RegexValidator(r'^[a-zA-Z]+$', '博客地址只能由英文组成'),
        ],
        widget=widgets.TextInput(attrs={"placeholder": "博客地址"})
    )
    theme = fields.CharField(
        widget=widgets.Select()
    )
    sammary = fields.CharField(
        max_length=64,
        required=False,
        strip=True,
        widget=widgets.Textarea(attrs={'cols': "110", 'rows': "6"})
    )

    # 动态获取数据库字段
    def __init__(self, *args, **kwargs):
        super(PersonnelForm, self).__init__(*args, **kwargs)
        self.fields['theme'].widget.choices = models.Blog.objects.values_list('theme', 'theme')






