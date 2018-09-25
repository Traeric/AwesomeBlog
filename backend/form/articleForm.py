from django.forms import forms, fields, widgets
from repository import models


# 撰写文章的表单
class ArticleForm(forms.Form):
    article_id = fields.IntegerField(required=False, widget=widgets.TextInput(attrs={"type": 'hidden'}))
    title = fields.CharField(
        required=True,
        strip=True,
        widget=widgets.TextInput(attrs={"class": 'form-control'})
    )
    summary = fields.CharField(
        required=True,
        strip=True,
        widget=widgets.Textarea(attrs={"class": 'form-control', "rows": 3})
    )
    detail = fields.CharField(
        required=True,
        strip=True,
        widget=widgets.Textarea(attrs={"id": "content"})
    )
    main_stack_category = fields.CharField(
        required=True,
        widget=widgets.RadioSelect()
    )
    category_id = fields.CharField(
        required=True,
        widget=widgets.RadioSelect()
    )
    tag_id = fields.CharField(
        required=True,
        widget=widgets.SelectMultiple()
    )

    # 动态获取数据库字段
    def __init__(self, blog_id, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.blog_id = blog_id
        self.fields['main_stack_category'].widget.choices = models.Article.category_choice
        self.fields['category_id'].widget.choices = (models.Category.
                                                     objects.filter(blog_id=self.blog_id).values_list("id", "caption"))
        self.fields['tag_id'].widget.choices = (models.Tag.
                                                objects.filter(blog_id=self.blog_id).values_list("id", "caption"))






