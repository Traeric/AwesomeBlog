from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.User)
admin.site.register(models.Blog)
admin.site.register(models.ThumbUp)
admin.site.register(models.Article)
admin.site.register(models.Category)
admin.site.register(models.Comment)
admin.site.register(models.Tag)
admin.site.register(models.Trouble)
admin.site.register(models.Role)
admin.site.register(models.Action)
admin.site.register(models.Menu)
admin.site.register(models.Permission)
admin.site.register(models.Permission2Action)
admin.site.register(models.Permission2Action2Role)
admin.site.register(models.User2Role)


