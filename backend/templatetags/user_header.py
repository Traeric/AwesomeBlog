from django import template
from repository import models


register = template.Library()


@register.filter
def user_header(nid):
    return '\\' + str(models.User.objects.filter(id=nid)[0].img)




