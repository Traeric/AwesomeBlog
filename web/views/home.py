from django.shortcuts import render, redirect
from repository import models
from django.urls import reverse
from utils.pageNation import Pagenation


# Create your views here.


# Global variable
PER_PAGE = 5     # 每一页显示的数目
MOST_COMMENTS = 8   # 评论最多的文章


# 跳转到主页面
def to_home(request):
    # 获取主页面的url
    path = reverse("home", kwargs={"category": 0})
    return redirect(path)


# 博客主页
def home(request, category):
    # 获取用户信息
    user_info = request.session.get("user", None)
    # 获取用户后缀
    if user_info:
        blog = models.Blog.objects.filter(user_id=user_info['id'])
        if blog:
            user_surfix = blog[0].surfix
        else:
            user_surfix = ''
    else:
        user_surfix = ''
    # 获取前端参数
    params = request.GET.get("page", None)
    try:
        current_page = int(params)
        if current_page <= 0:
            current_page = 1
    except TypeError:
        current_page = 1
    # 获取主站类型,并判断category是否超出了主站能表示范围
    stack_choices = models.Article.category_choice
    category_num = int(category)
    for i in stack_choices:
        if i[0] == category_num:
            break
    else:
        category_num = 0
    # 获取对应主站的文章
    if category_num == 0:
        articles = models.Article.objects.all()
    else:
        articles = models.Article.objects.filter(main_stack_category=category_num)
    # 准备分页
    url = reverse("home", kwargs={"category": category_num})    # 获取当前视图函数对应的url
    page_nation = Pagenation(articles.count(), current_page, PER_PAGE, url=url)   # 创建分页对象
    articles = articles[page_nation.start_index:page_nation.end_index]   # 获取当前页要展示的文章

    # 获取评论最多的文章
    sql = """
        SELECT a.id, a.title, a.user_id FROM article AS a, 
        (SELECT article_id, count(*) as num FROM comment GROUP BY article_id) As c WHERE
        a.id = c.article_id ORDER BY c.num DESC LIMIT 0, %s
    """
    comments_articles = models.Article.objects.raw(sql, params=[MOST_COMMENTS, ])

    return render(request, "home/home.html", {
        "articles": articles,
        "stack_choices": stack_choices,
        "current_category": category_num,
        "page_nation": page_nation,
        "user_info": user_info,
        'user_surfix': user_surfix,
        'comments_info': comments_articles
    })




