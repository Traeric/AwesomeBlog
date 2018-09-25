from copy import deepcopy

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from repository import models
from utils.pageNation import Pagenation
from backend.form.articleForm import ArticleForm
from utils.menu import permission, MenuCreater
from backend.form.personnelForm import PersonnelForm
import os
import uuid

# GLOBAL VARIBLE
PER_PAGE = 10
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# 获取展示菜单的字符串
def get_menu_str(request):
    # 获取菜单字符串
    menu_string = request.session.get('menu_string', None)
    if not menu_string:
        user_id = request.session['user'].get('id')
        obj = MenuCreater(request, user_id)
        menu_string = obj.menu_tree()
        request.session['menu_string'] = menu_string
    return menu_string


# 后台管理主页
def index(request):
    status = [-1, -1]
    # 获取用户信息
    user = request.session['user']
    return render(request, "backend/home.html", {
        'status': status,
        'user_info': user,
        'menu_string': get_menu_str(request)
    })


# 文章管理页面
@permission
def article(request, main_stack, category, *args, **kwargs):
    # 页面展示所需参数
    status = [0, 0]
    path = ['知识库管理', '文章']
    user = request.session['user']
    # 查询文章
    try:
        articles = models.Article.objects.filter(user_id=user['id'])
        total_count = articles.count()
        blog = models.Blog.objects.get(user_id=user['id'])
        # 文章类型选择
        # 处理两个分类参数
        # 处理主站分类
        stack_category = models.Article.category_choice
        try:
            main_stack_num = int(main_stack)
            category_num = int(category)
        except Exception:
            main_stack_num = 0
            category_num = 0

        for cg in stack_category:
            if cg[0] == main_stack_num:
                break
        else:
            main_stack_num = 0
        # 处理个人分类
        personnal_category = models.Category.objects.filter(blog=blog).values('id', "caption")
        for cg in personnal_category:
            if cg["id"] == category_num:
                break
        else:
            category_num = 0
        # 获取同时满足两个分类条件的文章
        if category_num != 0 and main_stack_num != 0:
            articles = articles.filter(main_stack_category=main_stack_num, category_id=category_num)
        elif category_num == 0 and main_stack_num != 0:
            articles = articles.filter(main_stack_category=main_stack_num)
        elif category_num != 0 and main_stack_num == 0:
            articles = articles.filter(category_id=category_num)
        # 准备分页
        url = reverse('article_page_nation')
        page_obj = Pagenation(articles.count(), 1, PER_PAGE, url=url)
        articles = articles[page_obj.start_index:page_obj.end_index]
        return render(request, "backend/articles.html", {
            'status': status,
            'user_info': user,
            'paths': path,
            'articles': articles,
            'blog': blog,
            'page_obj': page_obj,
            "total_count": total_count,
            "main_stack": stack_category,
            "personnel_category": personnal_category,
            'main_stack_num': main_stack_num,
            "category_num": category_num,
            'menu_string': get_menu_str(request)
        })
    except Exception:
        # 还没有开通博客
        url = reverse('personnel')
        return redirect(to=url)


# 文章分页
def article_page_nation(request):
    # 获取用户
    user = request.session['user']
    # 获取当前页数
    page = request.POST.get("page", None)
    try:
        page_num = int(page)
        if page_num < 0:
            page_num = 1
    except Exception:
        page_num = 1
    # 查询文章
    articles = models.Article.objects.filter(user_id=user['id'])
    blog = models.Blog.objects.get(user_id=user['id'])
    # 准备分页
    url = reverse('article_page_nation')
    page_obj = Pagenation(articles.count(), page_num, PER_PAGE, url=url)
    articles = articles[page_obj.start_index:page_obj.end_index]
    return render(request, "backend/article_page_nation.html", {
        'articles': articles,
        'page_obj': page_obj,
        'blog': blog,
    })


# 添加文章
def add_article(request):
    # 页面展示所需参数
    status = [0, 0]
    path = ['知识库管理', '文章', '操作文章']
    # 获取用户
    user = request.session['user']
    blog = models.Blog.objects.get(user_id=user['id'])
    # 创建表单对象
    article_form = ArticleForm(blog.id)
    # 保存文章
    if request.method == "POST":
        # 创建文章表单
        article_form = ArticleForm(blog.id, request.POST)
        kwargs = deepcopy(request.POST)
        # 处理标签
        # 获取标签
        tag = request.POST.getlist("tag_id")
        # 从数据库中取出这些标签
        tags = models.Tag.objects.filter(id__in=tag)
        # 添加到数据库
        dic = {
            "title": kwargs['title'],
            "summary": kwargs['summary'],
            "detail": kwargs["detail"],
            "main_stack_category": kwargs['main_stack_category'][0],
            "category_id": None if not kwargs.get('category_id', None) else kwargs['category_id'][0],
            "user_id": user['id']
        }
        try:
            print(kwargs['article_id'])
            if kwargs['article_id']:
                modify_articles = models.Article.objects.filter(id=int(kwargs['article_id']))
                modify_articles.update(**dic)
                add_articles = modify_articles[0]
            else:
                add_articles = models.Article.objects.create(**dic)
            # 添加关联
            add_articles.tag.add(*tags)
            url = reverse("article", kwargs={"main_stack": 0, "category": 0})
            return redirect(url)
        except Exception as e:
            print(e)
            return render(request, "backend/write_article.html", {
                'status': status,
                "user_info": user,
                'paths': path,
                "article_form": article_form,
                'menu_string': get_menu_str(request),
            })
    return render(request, "backend/write_article.html", {
        'status': status,
        "user_info": user,
        'paths': path,
        "article_form": article_form,
        'menu_string': get_menu_str(request),
    })


# 修改文章
def modify_article(request, article_id):
    # 页面展示所需参数
    status = [0, 0]
    path = ['知识库管理', '文章', '操作文章']
    # 获取用户
    user = request.session['user']
    blog = models.Blog.objects.get(user_id=user['id'])
    # 处理参数
    try:
        article_id_num = int(article_id)
        if article_id_num < 1:
            article_id_num = 1
    except Exception:
        article_id_num = 1
    # 获取文章参数
    mo_article = models.Article.objects.get(id=article_id_num)
    # 将文章信息传入表单
    tag_list = tuple(*zip(*list(mo_article.tag.values_list('id'))))
    article_form = ArticleForm(blog.id, {
        "article_id": mo_article.id,
        "title": mo_article.title,
        "summary": mo_article.summary,
        "detail": mo_article.detail,
        "main_stack_category": mo_article.main_stack_category,
        "category_id": mo_article.category_id,
        "tag_id": tag_list,
    })
    return render(request, "backend/write_article.html", {
        'status': status,
        "user_info": user,
        'paths': path,
        "article_form": article_form,
        'menu_string': get_menu_str(request),
    })


# 搜索文章
def search_article(request):
    # 获取用户
    user = request.session['user']
    # 获取要搜索的文章名
    article_name = request.POST.get('value', None)
    # 搜索文章
    try:
        articles = models.Article.objects.filter(user_id=user['id'], title__icontains=article_name)
        blog = models.Blog.objects.get(user_id=user['id'])
        # 准备分页
        url = reverse('article_page_nation')
        page_obj = Pagenation(articles.count(), 1, PER_PAGE, url=url)
        articles = articles[page_obj.start_index:page_obj.end_index]
        return render(request, "backend/article_page_nation.html", {
            'articles': articles,
            'page_obj': page_obj,
            'blog': blog,
        })
    except Exception:
        return HttpResponse('<h1>404 NOT FOUND</h1>')


# 分类管理首页
def category(request):
    # 页面展示所需参数
    status = [0, 1]
    path = ['知识库管理', '分类管理']
    user = request.session['user']
    dic = {
        'status': status,
        "user_info": user,
        'paths': path,
        'menu_string': get_menu_str(request),
    }
    # 获取所有的分类
    try:
        blog = models.Blog.objects.get(user_id=user['id'])
        dic['blog'] = blog
        categorys = blog.category_set.all()
        dic['categorys'] = categorys
        return render(request, "backend/category.html", dic)
    except Exception:
        url = reverse("personnel")
        return redirect(to=url)


# 添加分类
def add_category(request):
    # 获取用户
    user = request.session['user']
    # 获取分类名称
    category_name = request.POST.get('categoryName', None)
    # 添加分类
    try:
        blog = models.Blog.objects.get(user_id=user['id'])
        models.Category.objects.create(blog=blog, caption=category_name)
    except Exception:
        return HttpResponse('0')
    return HttpResponse('1')


# 删除分类
def delete_category(request):
    # 获取用户
    user = request.session['user']
    # 获取要删除标签的id
    nid = request.GET.get('categoryId', None)
    # 进行删除
    try:
        blog = models.Blog.objects.get(id=user['id'])
        models.Category.objects.filter(blog=blog, id=nid).delete()
    except Exception:
        return HttpResponse('去你妈的')
    url = reverse("category")
    return redirect(to=url)


# 修改分类
def modify_category(request):
    # 获取用户
    user = request.session['user']
    # 获取标签id跟标签名
    nid = request.POST.get('tagId', None)
    caption = request.POST.get('caption', None)
    # 进行修改
    try:
        blog = models.Blog.objects.get(user_id=user['id'])
        models.Category.objects.filter(blog=blog, id=nid).update(caption=caption)
    except Exception:
        return HttpResponse('0')
    return HttpResponse('1')


# 标签管理展示页面
def tag(request):
    # 页面展示所需参数
    status = [0, 2]
    path = ['知识库管理', '标签管理']
    user = request.session['user']
    dic = {
        'status': status,
        "user_info": user,
        'paths': path,
        'menu_string': get_menu_str(request),
    }
    # 获取所有的标签
    try:
        blog = models.Blog.objects.get(user_id=user['id'])
        dic['blog'] = blog
        tags = blog.tag_set.all()
        dic['tags'] = tags
        return render(request, "backend/tag.html", dic)
    except Exception:
        url = reverse('personnel')
        return redirect(to=url)


# 添加标签
def add_tag(request):
    # 获取用户名
    user = request.session['user']
    # 获取标签名
    tag_name = request.POST.get("tagName", None)
    try:
        blog = models.Blog.objects.get(user_id=user['id'])
        models.Tag.objects.create(caption=tag_name, blog=blog)
    except Exception:
        return HttpResponse('0')
    return HttpResponse('1')


# 删除标签
def delete_tag(request):
    # 获取用户
    user = request.session['user']
    # 获取要删除标签的id
    nid = request.GET.get('tagId', None)
    # 进行删除
    try:
        blog = models.Blog.objects.get(id=user['id'])
        models.Tag.objects.filter(blog=blog, id=nid).delete()
    except Exception:
        return HttpResponse('去你妈的')
    url = reverse("tag")
    return redirect(to=url)


# 修改标签
def modify_tag(request):
    # 获取用户
    user = request.session['user']
    # 获取标签id跟标签名
    nid = request.POST.get('tagId', None)
    caption = request.POST.get('caption', None)
    # 进行修改
    try:
        blog = models.Blog.objects.get(user_id=user['id'])
        models.Tag.objects.filter(blog=blog, id=nid).update(caption=caption)
    except Exception:
        return HttpResponse('0')
    return HttpResponse('1')


# 个人信息首页
def personnel(request):
    # 页面展示所需参数
    status = [0, 3]
    path = ['知识库管理', '个人信息']
    user = request.session['user']
    dic = {
        'status': status,
        "user_info": user,
        'paths': path,
        'menu_string': get_menu_str(request),
    }
    # 获取博客信息
    blog = models.Blog.objects.filter(user_id=user['id'])
    dic['blog'] = blog
    # 初始化个人信息表单
    kwargs = {
        'user_name': user['username'],
        'email': user['email'],
        'blog_title': blog[0].title if len(blog) > 0 else '',
        'blog_surfix': blog[0].surfix if len(blog) > 0 else '',
        'theme': blog[0].theme if len(blog) > 0 else '',
        'sammary': blog[0].summary if len(blog) > 0 else ''
    }
    personnel_form = PersonnelForm(initial=kwargs)
    dic['p_form'] = personnel_form
    return render(request, 'backend/personnel.html', dic)


# 修改个人信息
def modify_personnel(request):
    # 页面展示所需参数
    status = [0, 3]
    path = ['知识库管理', '个人信息']
    user = request.session['user']
    dic = {
        'status': status,
        "user_info": user,
        'paths': path,
        'menu_string': get_menu_str(request),
    }
    # 初始化个人信息表单
    p_form = PersonnelForm(request.POST)
    # 验证
    if p_form.is_valid():
        # 验证成功, 获取用户输入数据
        data = p_form.cleaned_data
        # 将数据存入数据库
        try:
            blog = models.Blog.objects.filter(user_id=user['id'])
            if blog.count():   # 已经开通了博客
                (blog.update(title=data['blog_title'], surfix=data['blog_surfix'],
                             theme=data['theme'], summary=data['sammary']))
            else:      # 未开通博客
                (models.Blog.objects.create(user_id=user['id'], title=data['blog_title'],
                                            surfix=data['blog_surfix'], theme=data['theme'],
                                            summary=data['sammary']))
            # 保存用户相关信息
            (models.User.objects.filter(id=user['id']).update(username=data['user_name'],
                                                              email=data['email']))
            dic['p_form'] = PersonnelForm(data)
            return render(request, 'backend/personnel.html', dic)
        except Exception:
            return HttpResponse('服务器开小差啦~~~')
    else:
        dic['p_form'] = p_form
        return render(request, 'backend/personnel.html', dic)


# 提交头像
def set_header(request):
    user = request.session['user']
    # 获取图片
    img = request.FILES.get('header_img')
    # 将图片存到本地
    surfix_arr = img.name.split(".")
    file_name = str(uuid.uuid4()) + '.' + surfix_arr[len(surfix_arr)-1]
    path = os.path.join('static', 'user_data', file_name)
    with open(path, 'wb') as f:
        for img_chunk in img.chunks():
            f.write(img_chunk)
    # 将图片地址存到数据库
    models.User.objects.filter(id=user['id']).update(img=path)
    return HttpResponse(path)




