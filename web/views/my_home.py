from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse

from repository import models
from utils.pageNation import Pagenation
import json

PER_PAGE = 5


# 将查询全部和查询某个分类的共同部分封装起来
def base(surfix):
    # 选出该后缀对应的博客表以及关联的用户
    blog = models.Blog.objects.filter(surfix=surfix).select_related('user').first()  # 只进行一次查询
    if not blog:
        path = reverse("home", kwargs={"category": 0})
        return redirect(path)
    # 筛选出对应的时间文章
    article_by_time = models.Article.objects.raw("SELECT id, COUNT(id) AS num, DATE_FORMAT(ctime, '%%Y-%%m') "
                                                 "AS create_time, user_id FROM Article WHERE user_id={0} "
                                                 "GROUP BY create_time".format(blog.user_id))

    articles = models.Article.objects.filter(user=blog.user)
    return {
        "blog": blog,
        "article_by_time": article_by_time,
        "articles": articles
    }


# 博客个人主页————显示全部文章
def my_home(request, surfix):
    dic = base(surfix)
    return render(request, "my_home/my_home.html", dic)


# 博客个人主页————筛选文章
def article_filter(request, surfix, category, num):
    dic = base(surfix)
    # 进行分类
    if category == "tag":
        # 查询出该tag下的所有文章
        tag = models.Tag.objects.get(id=num)
        articles = models.Article.objects.filter(tag=tag, user=dic['blog'].user)
    elif category == 'category':
        # 查询出该category下的所有文章
        categorys = models.Category.objects.get(id=num)
        articles = models.Article.objects.filter(category=categorys, user=dic['blog'].user)
    else:
        articles = models.Article.objects.filter(user=dic['blog'].user).extra(
            where=['date_format(ctime, "%%Y-%%m")=%s'], params=[num, ])
    dic["articles"] = articles
    return render(request, "my_home/my_home.html", dic)


# 文章详情
def article_detail(request, surfix, article_id):
    dic = base(surfix)
    # 查询出该篇文章
    article = models.Article.objects.get(id=article_id)
    dic['article'] = article
    # 检查用户是否登录
    dic['is_login'] = True if request.session.get('user', None) else False
    # 获取评论
    comment = article.comment_set.all()
    # 给评论排序（将子评论插到父评论下）
    sorted_comment = sort_comment(comment)
    comments = sorted_comment[:PER_PAGE]
    dic['comments'] = comments
    # 给评论分页
    path = reverse("comment_page_nation")
    page_obj = Pagenation(len(sorted_comment), 1, PER_PAGE, url=path)
    dic['page_obj'] = page_obj
    return render(request, "my_home/article_detail.html", dic)


# 给评论排序
def sort_comment(comment_query):
    """
    [
        {
              id: 1,
              content: "",
              ctime: "",
              user: "",
              article: "",
              child: [
                  {
                      id: 1,
                      content: "",
                      ctime: "",
                      user: "",
                      article: "",
                      child: {...}
                  },
                  {...}
              ]
          },
        {...}
    ]
    :param comment_query:
    :return:
    """
    ret_dic = []   # 最终所有的评论都会放到这个数组里面
    dynamic_dic = {}   # 临时存放所有评论的字典
    for comment in comment_query:
        # 将querySet转成字典
        dynamic_dic[comment.id] = {
            'id': comment.id,
            'content': comment.content,
            'ctime': comment.ctime,
            'user': comment.user,
            'parent_id': comment.parent_comment_id,
            'child': [],
        }

    for comment in dynamic_dic.values():
        # 查看该条评论有没有父id，如果没有就把它放到根目录下
        if not comment['parent_id']:
            ret_dic.append(comment)
        else:
            # 如果有父id，就把该条评论放到父评论的child数组里面
            dynamic_dic[comment['parent_id']]['child'].append(comment)
    return ret_dic     # 返回这个数组


# 保存评论
def save_comment(request):
    message = dict()
    if request.session.get("user", None):
        # 获取评论内容
        comment_content = request.POST.get("comment_content", None)
        # 获取本篇文章的id
        article_id = request.POST.get("article_id", None)
        if comment_content:
            # 将评论存入数据库
            # 获取用户ID
            user_id = request.session['user']['id']
            try:
                models.Comment.objects.create(content=comment_content, user_id=int(user_id), article_id=int(article_id))
                message['status'] = True
                message['info'] = "评论成功"
            except Exception:
                message['status'] = False
                message['info'] = "数据插入失败"
        else:
            message['status'] = False
            message['info'] = '评论内容无效'
    else:
        message['status'] = False
        message['info'] = '未登录'
    return HttpResponse(json.dumps(message))


# 评论分页
def comment_page_nation(request):
    # 获取分页
    page = request.POST.get("page", None)
    if page:
        try:
            page_num = int(page)
        except Exception:
            page_num = 1
    else:
        page_num = 1
    # 查询属于该篇文章的该篇分页的评论数据
    article_id = request.POST.get("article_id")
    comment = models.Comment.objects.filter(article_id=article_id)
    # 给评论排序（将子评论插到父评论下）
    sorted_comment = sort_comment(comment)
    # 准备分页
    path = reverse("comment_page_nation")
    page_obj = Pagenation(len(sorted_comment), page_num, PER_PAGE, url=path)

    comments = sorted_comment[page_obj.start_index:page_obj.end_index]
    # 检查登录情况
    is_login = True if request.session.get('user', None) else False
    return render(request, "my_home/comment.html", {
        "comments": comments,
        "page_obj": page_obj,
        'is_login': is_login,
        'article_id': article_id,
    })


# 赞踩关系处理
def thumb(request):
    # 获取文章id
    article_id = request.POST.get('article_id', None)
    # 获取用户
    user = request.session['user']
    # 是否点赞
    is_thumb_up = bool(int(request.POST.get('is_thumb_up')))
    # 将点赞信息储存
    try:
        models.ThumbUp.objects.create(article_id=article_id, user_id=user['id'], is_thumb_up=is_thumb_up)
    except:
        return HttpResponse(0)
    return HttpResponse(1)


# 回复评论
def re_comment(request):
    # 获取评论信息
    parent_id = request.POST.get("parent_id", None)
    comment_content = request.POST.get("comment_content", None)
    article_id = request.POST.get("article_id", None)
    # 获取用户
    user = request.session['user']
    # 将评论存到数据库
    try:
        models.Comment.objects.create(
            content=comment_content,
            user_id=user['id'],
            article_id=article_id,
            parent_comment_id=parent_id,
        )
    except:
        return HttpResponse("0")
    return HttpResponse("1")

