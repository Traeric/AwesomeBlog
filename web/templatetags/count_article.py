from django import template
from repository import models

register = template.Library()


@register.filter
def count_tag(tag, user):
    return models.Article.objects.filter(user=user, tag=tag).count()


@register.filter
def count_category(category, user):
    return models.Article.objects.filter(user=user, category=category).count()


# 通过用户id找到用户后缀
@register.filter
def surfix_by_user(user_id):
    # 根据user_id获取surfix
    return models.User.objects.filter(id=user_id)[0].blog.surfix


# 通过文章id获取博客后缀
@register.filter
def surfix_by_article(article_id):
    user = models.Article.objects.filter(id=article_id)[0].user
    return models.Blog.objects.filter(user=user)[0].surfix


# 获取用户点赞数
@register.filter
def get_thumb(article_id):
    # 返回文章点赞数
    return models.ThumbUp.objects.filter(article_id=article_id, is_thumb_up=True).count()


# 获取用户踩文章数
@register.filter
def get_thumb_down(article_id):
    # 返回文章点赞数
    return models.ThumbUp.objects.filter(article_id=article_id, is_thumb_up=False).count()





