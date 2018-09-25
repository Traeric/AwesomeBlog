from django.db import models


# 用户信息表
class User(models.Model):
    username = models.CharField(max_length=16, unique=True, verbose_name="用户名")
    pwd = models.CharField(max_length=32, verbose_name="密码")
    email = models.CharField(max_length=32, unique=True, verbose_name="邮箱")
    img = models.CharField(verbose_name="头像", null=True, blank=True, max_length=256)
    fans = models.ManyToManyField(to="User", related_name="refans", blank=True)

    class Meta:
        verbose_name_plural = "用户表"
        db_table = "User"

    def __str__(self):
        return self.username


# 博客表
class Blog(models.Model):
    theme = models.CharField(max_length=8, verbose_name="博客主题", blank=True, null=True)
    title = models.CharField(max_length=16, verbose_name="博客标题", blank=True, null=True)
    summary = models.CharField(max_length=64, verbose_name="基本简介", blank=True, null=True)
    surfix = models.CharField(max_length=32, verbose_name="后缀", unique=True)
    user = models.OneToOneField(to="User", to_field="id", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "博客表"
        db_table = "Blog"


# 分类表
class Category(models.Model):
    caption = models.CharField(max_length=8, unique=True, verbose_name="类别")
    blog = models.ForeignKey(to="Blog", to_field="id", on_delete=models.CASCADE)

    def __str__(self):
        return self.caption

    class Meta:
        db_table = "Category"
        verbose_name_plural = "分类表"


# 标签表
class Tag(models.Model):
    caption = models.CharField(max_length=8, unique=True, verbose_name="标签类别")
    blog = models.ForeignKey(to="Blog", to_field="id", on_delete=models.CASCADE)

    def __str__(self):
        return self.caption

    class Meta:
        db_table = "Tag"
        verbose_name_plural = "标签表"


# 文章表
class Article(models.Model):
    title = models.CharField(max_length=16, verbose_name="标题")
    summary = models.CharField(max_length=256, verbose_name="基本简介")
    detail = models.TextField(verbose_name="具体文章")
    ctime = models.DateTimeField(auto_now=True, verbose_name="创建时间")
    category_choice = ((1, "Python"), (2, "Golang"), (3, "Linux运维"), (4, "Java"), )
    main_stack_category = models.IntegerField(choices=category_choice, verbose_name="主站分类")
    category = models.ForeignKey(to="Category", to_field='id', on_delete=models.CASCADE, null=True, blank=True)
    tag = models.ManyToManyField(to="Tag", blank=True)
    user = models.ForeignKey(to="User", to_field='id', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "Article"
        verbose_name_plural = "文章表"


# 赞踩文章关系表
class ThumbUp(models.Model):
    article = models.ForeignKey(to="Article", to_field="id", verbose_name="文章id", on_delete=models.CASCADE)
    user = models.ForeignKey(to="User", to_field='id', verbose_name="用户ID", on_delete=models.CASCADE)
    is_thumb_up = models.BooleanField()

    class Meta:
        db_table = "ThumbUp"
        verbose_name_plural = "赞踩文章关系表"
        unique_together = (("article", "user"), )


# 评论表
class Comment(models.Model):
    content = models.TextField(verbose_name="评论内容")
    ctime = models.DateTimeField(auto_now=True, verbose_name="评论时间")
    user = models.ForeignKey(to="User", to_field='id', on_delete=models.CASCADE, verbose_name="评论人")
    article = models.ForeignKey(to="Article", to_field='id', on_delete=models.CASCADE, verbose_name="评论文章")
    parent_comment = models.ForeignKey(to="Comment", to_field='id', on_delete=models.CASCADE,
                                       verbose_name="父评论", null=True, blank=True)

    def __str__(self):
        return self.user.username + "--->" + self.content

    class Meta:
        db_table = "Comment"
        verbose_name_plural = "评论表"


# 报障表
class Trouble(models.Model):
    title = models.CharField(max_length=64, verbose_name="报障标题")
    detail = models.TextField(verbose_name="故障描述")
    sender = models.ForeignKey(to="User", to_field="id", on_delete=models.CASCADE, related_name="sender", verbose_name="提交者")
    ctime = models.CharField(max_length=32, verbose_name="创建时间")
    status_choices = ((1, "未处理"), (2, "处理中"), (3, "已处理"), )
    status = models.IntegerField(choices=status_choices, verbose_name="障单状态")
    handler = models.ForeignKey(to="User", to_field="id", on_delete=models.CASCADE, null=True, blank=True)
    solve_plan = models.TextField(verbose_name="解决方案", null=True, blank=True)
    stime = models.CharField(max_length=32, verbose_name="解决时间", null=True, blank=True)
    evaluate_choices = ((1, "活儿不行"), (2, "一般"), (3, "活儿很好"), )
    evaluate = models.IntegerField(choices=evaluate_choices, verbose_name="评价", null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "Trouble"
        verbose_name_plural = "报障表"


# 权限管理相关表


# 角色表
class Role(models.Model):
    caption = models.CharField(max_length=32)

    class Meta:
        db_table = "role"
        verbose_name_plural = '角色表'

    def __str__(self):
        return self.caption


# 用户角色关联表
class User2Role(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        db_table = "user2role"
        verbose_name_plural = '用户分配角色'

    def __str__(self):
        return "%s-%s" % (self.user.username, self.role.caption,)


# 权限表
class Action(models.Model):
    # get  获取用户信息1
    # post  创建用户2
    # delete 删除用户3
    # put  修改用户4
    caption = models.CharField(max_length=32)
    code = models.CharField(max_length=32)

    class Meta:
        db_table = 'action'
        verbose_name_plural = '操作表'

    def __str__(self):
        return self.caption


# 1    菜单1     null
# 2    菜单2     null
# 3    菜单3     null
# 4    菜单1.1    1
# 5    菜单1.2    1
# 6    菜单1.2.1  4
# 无最后一层
class Menu(models.Model):
    caption = models.CharField(max_length=32)
    parent = models.ForeignKey('self', related_name='p', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % (self.caption,)


# URL表
class Permission(models.Model):
    # http://127.0.0.1:8001/user.html  用户管理 1
    # http://127.0.0.1:8001/order.html 订单管理 1
    caption = models.CharField(max_length=32)
    url = models.CharField(max_length=64)
    menu = models.ForeignKey(Menu, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'permission'
        verbose_name_plural = 'URL表'

    def __str__(self):
        return "%s-%s" % (self.caption, self.url,)


# URL跟权限关联表
class Permission2Action(models.Model):
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '权限表'

    def __str__(self):
        return "%s-%s:-%s?t=%s" % (self.permission.caption, self.action.caption, self.permission.url, self.action.code,)


# 角色跟权限关联表
class Permission2Action2Role(models.Model):
    p2a = models.ForeignKey(Permission2Action, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '角色分配权限'

    def __str__(self):
        return "%s==>%s" % (self.role.caption, self.p2a,)





