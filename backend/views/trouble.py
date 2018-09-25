from django.db.models import Q
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse

from repository import models
from backend.form.troubleForm import TroubleForm
from backend.form.handleTroubleForm import HandleTroubleForm
from backend.form.solvePlanForm import SolvePlanForm
from utils.menu import permission, MenuCreater
from utils.pageNation import Pagenation
import datetime
import json
import copy


# 全局变量
PER_PAGE = 10


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


# 装饰器处理分页
def handle_page(func):
    def inner(request, *args, **kwargs):
        # 获取当前页数
        page = request.POST.get("page", None)
        print(page)
        try:
            page_num = int(page)
            if page_num < 0:
                page_num = 1
        except Exception:
            page_num = 1
        return func(request, page_num, *args, **kwargs)
    return inner


# 展示报障单
@permission
def display_trouble_list(request, *args, **kwargs):
    # 页面展示所需参数
    status = [1, 0]
    path = ['报障管理', '个人报障']
    user = request.session['user']
    # 获取所有的报障单
    trouble_list = models.Trouble.objects.filter(sender_id=user['id']).order_by("status").only("id", "title", "status")
    # 准备分页
    url = reverse('display_pagenation')
    page_obj = Pagenation(trouble_list.count(), 1, PER_PAGE, url=url)
    trouble_list = trouble_list[page_obj.start_index:page_obj.end_index]
    return render(request, "backend/display_trouble.html", {
        'status': status,
        'user_info': user,
        'paths': path,
        "trouble_list": trouble_list,
        "page_obj": page_obj,
        'menu_string': get_menu_str(request)
    })


# 报障单分页
@handle_page
def display_trouble_page_nation(request, page_num):
    # 获取用户
    user = request.session["user"]
    # 查询报障单
    trouble_list = models.Trouble.objects.filter(sender_id=user['id']).order_by('status').only("id", "title", "status")
    # 准备分页
    url = reverse('display_pagenation')
    page_obj = Pagenation(trouble_list.count(), page_num, PER_PAGE, url=url)
    trouble_list = trouble_list[page_obj.start_index:page_obj.end_index]
    return render(request, "backend/trouble_list_page_nation.html", {
        "trouble_list": trouble_list,
        "page_obj": page_obj
    })


# 创建报障单
def create_trouble_list(request):
    # 页面展示所需参数
    status = [1, 0]
    path = ['报障管理', '个人报障', '创建报障单']
    user = request.session['user']
    dic = {
        'status': status,
        'user_info': user,
        'paths': path,
        'menu_string': get_menu_str(request),
    }
    # 获取有没有报障单的id
    trouble_id = request.GET.get("trouble_id", None)
    if trouble_id is not None:
        # 从数据库获取这条报障单的信息
        v = models.Trouble.objects.filter(id=trouble_id, status=1, sender_id=user['id'])
        if v:
            info = v.values("title", "detail")[0]
            param = {"trouble_id": trouble_id}
            param.update(dict(info))
        else:
            return HttpResponse("去你妈的。。。")
    else:
        param = {}
    # 创建报障表单
    trouble_form = TroubleForm(initial=param)
    dic["trouble_form"] = trouble_form
    return render(request, "backend/create_trouble.html", dic)


# 保存报障单
def save_trouble_list(request):
    # 页面展示所需参数
    status = [1, 0]
    path = ['报障管理', '个人报障', '创建报障单']
    # 获取用户
    user = request.session['user']
    # 创建表单
    trouble_form = TroubleForm(request.POST)
    # 验证
    if trouble_form.is_valid():
        # 验证成功，将信息添加到数据库
        try:
            dic = {
                "sender_id": user['id'],
                "ctime": datetime.datetime.now(),
                "status": 1,
                "title": trouble_form.cleaned_data["title"],
                "detail": trouble_form.cleaned_data['detail']
            }
            trouble_id = trouble_form.cleaned_data['trouble_id']
            if trouble_id:
                # 有说明是在修改
                # 先获取该账单的信息再更新
                v = models.Trouble.objects.filter(id=trouble_id, status=1).update(**dic)
                if not v:
                    return HttpResponse("别人已经接单了哦，所以不能修改了。。。")
            else:
                # 否则就是在新建
                models.Trouble.objects.create(**dic)
            url = reverse("display_trouble_list")
            return redirect(url)
        except Exception as e:
            print(e)
            return render(request, "backend/create_trouble.html", {
                'status': status,
                'user_info': user,
                'paths': path,
                "trouble_form": trouble_form,
                'menu_string': get_menu_str(request),
            })
    else:
        return render(request, "backend/create_trouble.html", {
            'status': status,
            'user_info': user,
            'paths': path,
            "trouble_form": trouble_form,
            'menu_string': get_menu_str(request),
        })


# 搜索报账单
def search_trouble_list(request):
    # 获取报账单的名称
    trouble_name = request.POST.get('value', None)
    # 获取用户
    user = request.session["user"]
    # 查询
    try:
        # 查询报障单
        trouble_list = (models.Trouble.objects.filter(sender_id=user['id'], title__icontains=trouble_name).
                        order_by('status').only("id", "title", "status"))
        # 准备分页
        url = reverse('display_pagenation')
        page_obj = Pagenation(trouble_list.count(), 1, PER_PAGE, url=url)
        trouble_list = trouble_list[page_obj.start_index:page_obj.end_index]
        return render(request, "backend/trouble_list_page_nation.html", {
            "trouble_list": trouble_list,
            "page_obj": page_obj
        })
    except Exception:
        return HttpResponse('<h1>404 NOT FOUND</h1>')


# 展示待处理的报障单
@permission
def display_handle_trouble_list(request, *args, **kwargs):
    # 页面展示所需参数
    status = [1, 1]
    path = ['报障管理', '处理报障单']
    user = request.session['user']
    dic = {
        'status': status,
        'user_info': user,
        'paths': path,
        'menu_string': get_menu_str(request),
    }
    # 获取未处理而且不是自己的报障单 或者 是自己接单但是未处理的 或者 是自己接单而且已经处理了的
    trouble_list = (models.Trouble.objects.filter(Q(Q(status=1) & ~Q(sender_id=user['id'])) |
                                                  Q(~Q(status=1) & Q(handler_id=user['id']))).order_by("status"))
    # 准备分页
    url = reverse("handle_trouble_page_nation")
    page_obj = Pagenation(trouble_list.count(), 1, PER_PAGE, url=url)
    dic['page_nation'] = page_obj
    trouble_list = trouble_list[page_obj.start_index:page_obj.end_index]
    dic['trouble_list'] = trouble_list
    return render(request, "backend/handle_trouble_list.html", dic)


# 处理报账单分页
@handle_page
def handle_trouble_page_nation(request, page_num):
    user = request.session['user']
    # 获取未处理而且不是自己的报障单 或者 是自己接单但是未处理的 或者 是自己接单而且已经处理了的
    trouble_list = (models.Trouble.objects.filter(Q(Q(status=1) & ~Q(sender_id=user['id'])) |
                                                  Q(~Q(status=1) & Q(handler_id=user['id']))).order_by("status"))
    # 准备分页
    url = reverse("handle_trouble_page_nation")
    page_obj = Pagenation(trouble_list.count(), page_num, PER_PAGE, url=url)
    trouble_list = trouble_list[page_obj.start_index:page_obj.end_index]
    return render(request, "backend/handle_trouble_page_nation.html", {
        "trouble_list": trouble_list,
        "page_nation": page_obj,
    })


# 抢单
def get_trouble_list(request):
    user = request.session['user']
    # 获取报障单的id
    trouble_id = request.POST.get("trouble_id", None)
    if trouble_id:
        # 填写解决人跟接单状态
        v = models.Trouble.objects.filter(id=trouble_id, status=1).update(handler_id=user['id'], status=2)
        if v:
            return HttpResponse("已接单，请尽快处理")
        else:
            return HttpResponse("手速太慢，订单已被别人接走")


# 书写处理方案
def handle_trouble_list(request):
    # 页面展示所需参数
    status = [1, 1]
    path = ['报障管理', '处理报障单', '解决方案']
    user = request.session['user']
    dic = {
        'status': status,
        'user_info': user,
        'paths': path,
        'menu_string': get_menu_str(request),
    }
    # 获取待解决的报障单的id
    trouble_id = request.GET.get('trouble_id', None)
    # 从数据库中获取该报障单的信息
    try:
        trouble = models.Trouble.objects.filter(id=trouble_id, status=2)
        if trouble.exists():
            handle_trouble_form = HandleTroubleForm(initial={"trouble_id": trouble_id, "title": trouble[0].title, "detail": trouble[0].detail})
            dic['handle_trouble_form'] = handle_trouble_form
            return render(request, "backend/handle_trouble_form.html", dic)
        else:
            return HttpResponse("未获取数据")
    except Exception:
        return HttpResponse("数据异常")


# 保存解决方案
def save_solve_plan(request):
    # 页面展示所需参数
    status = [1, 1]
    path = ['报障管理', '处理报障单', '解决方案']
    user = request.session['user']
    dic = {
        'status': status,
        'user_info': user,
        'paths': path,
        'menu_string': get_menu_str(request),
    }
    # 创建解决方案的表单
    handle_trouble_form = HandleTroubleForm(request.POST)
    # 检查问题
    if handle_trouble_form.is_valid():
        # 将数据保存到数据库
        # 获取报障单的id
        trouble_id = handle_trouble_form.cleaned_data['trouble_id']
        solve_plan = handle_trouble_form.cleaned_data['solve_plan']
        v = (models.Trouble.objects.filter(id=trouble_id, status=2, handler_id=user['id']).
             update(status=3, solve_plan=solve_plan, stime=datetime.datetime.now()))
        if v:
            url = reverse("display_handle_trouble_list")
            return redirect(url)
        else:
            return HttpResponse("去你妈的。。。")
    else:
        dic['handle_trouble_form'] = handle_trouble_form
        return render(request, "backend/handle_trouble_form.html", dic)


# 查看解决方案
def watch_solve_plan(request):
    # 页面展示所需参数
    path = ['报障管理', '个人报障', '查看解决方案']
    user = request.session['user']
    dic = {
        'user_info': user,
        'paths': path,
        'menu_string': get_menu_str(request),
    }
    # 获取报障单的id
    trouble_id = request.GET.get("trouble_id", None)
    try:
        status = [1, 0]
        dic["status"] = status
        # 提交人查看
        trouble = models.Trouble.objects.filter(id=trouble_id, status=3, sender_id=user['id'])[0]
        # 实例化解决方案的表单
        solve_plan_form = SolvePlanForm({"trouble_id": trouble_id})
        dic['trouble'] = trouble
        dic['solve_plan_form'] = solve_plan_form
        dic['user'] = 0
        return render(request, "backend/watch_solve_plan.html", dic)
    except Exception:
        try:
            status = [1, 1]
            dic["status"] = status
            # 处理人查看
            trouble = models.Trouble.objects.filter(id=trouble_id, status=3, handler_id=user['id'])[0]
            # 实例化解决方案的表单
            solve_plan_form = SolvePlanForm({"trouble_id": trouble_id})
            dic['trouble'] = trouble
            dic['solve_plan_form'] = solve_plan_form
            dic['user'] = 1
            return render(request, "backend/watch_solve_plan.html", dic)
        except Exception:
            return HttpResponse("数据异常")


# 评价
def evaluate(request):
    user = request.session['user']
    # 创建评价表单
    solve_plan_form = SolvePlanForm(request.POST)
    if solve_plan_form.is_valid():
        # 获取待评论的报障单的id
        trouble_id = solve_plan_form.cleaned_data['trouble_id']
        v = (models.Trouble.objects.filter(status=3, id=trouble_id, sender_id=user['id']).
             update(evaluate=solve_plan_form.cleaned_data['evaluate']))
        if v:
            url = reverse("display_trouble_list")
            return redirect(url)
        else:
            return HttpResponse("去你妈的。。。")

    else:
        return HttpResponse("数据异常")


# 搜索待处理的报账单
def search_handle_trouble(request):
    # 获取要搜索的报账单名称
    handle_trouble = request.POST.get('value', None)
    # 获取用户
    user = request.session['user']
    # 开始搜索
    try:
        # 获取未处理而且不是自己的报障单 或者 是自己接单但是未处理的 或者 是自己接单而且已经处理了的
        trouble_list = (models.Trouble.objects.filter((Q(Q(status=1) & ~Q(sender_id=user['id'])) |
                                                      Q(~Q(status=1) & Q(handler_id=user['id']))),
                                                      title__icontains=handle_trouble).order_by("status"))
        # 准备分页
        url = reverse("handle_trouble_page_nation")
        page_obj = Pagenation(trouble_list.count(), 1, PER_PAGE, url=url)
        trouble_list = trouble_list[page_obj.start_index:page_obj.end_index]
        return render(request, "backend/handle_trouble_page_nation.html", {
            "trouble_list": trouble_list,
            "page_nation": page_obj,
        })
    except Exception:
        return HttpResponse('<h1>404 NOT FOUND</h1>')


# 画报障信息图
@permission
def draw_trouble(request, *args, **kwargs):
    status = [1, 2]
    path = ['报障管理', '报障信息统计']
    user = request.session['user']
    dic = {
        'status': status,
        'user_info': user,
        'paths': path,
        'menu_string': get_menu_str(request)
    }
    return render(request, "backend/draw_trouble.html", dic)


# 获取数据
def get_data(request):
    # 先查询出所有的管理员
    administrators = models.User.objects.filter()
    # 再查询出每个人对应月份处理的报障单数量
    ret_dic = []
    for administrator in administrators:
        ret = models.Trouble.objects.raw("SELECT id, COUNT(id) AS num, unix_timestamp(DATE_FORMAT(stime, '%%Y-%%m-01'))*1000+2592000000 "
                                         "AS solve_time FROM Trouble WHERE handler_id = %s "
                                         "GROUP BY DATE_FORMAT(stime, '%%Y-%%m')", params=[administrator.id, ])
        array = []
        for r in ret:
            if r.solve_time is not None:
                array.append([r.solve_time, r.num])
        ret_dic.append({
            'name': administrator.username,
            'data': array
        })
    return HttpResponse(json.dumps(ret_dic))


# 分配权限
@permission
def giving_action(request, *args, **kwargs):
    status = [2, 0]
    path = ['权限管理', '分配权限']
    user = request.session['user']
    dic = {
        'status': status,
        'user_info': user,
        'paths': path,
        'menu_string': get_menu_str(request)
    }
    # 获取所有的除了超级用户以外的所有用户
    u2r = models.User2Role.objects.exclude(role__id=1)
    users = None
    for u in u2r:
        if not users:
            users = copy.deepcopy(list(models.User.objects.filter(user2role=u)))
        else:
            new_users = list(models.User.objects.filter(user2role=u))
            # 进行去重
            for user in users:
                if user in new_users:
                    new_users.remove(user)
            users = users + new_users
    dic['users'] = users
    # 获取所有的角色
    roles = models.Role.objects.all()
    dic['roles'] = roles
    return render(request, 'backend/giving_action.html', dic)


# 保存角色
def save_role(request):
    user_id = request.POST.get('userId', None)
    role_list = request.POST.getlist('roleList')
    try:
        # 修改用户角色
        user = models.User.objects.get(id=user_id)
        # 首先删除以前的用户关联角色
        models.User2Role.objects.filter(user=user).delete()
        # 然后添加角色
        for role in role_list:
            models.User2Role.objects.create(user=user, role_id=role)
    except Exception:
        return HttpResponse('0')
    return HttpResponse('1')


# 搜索角色
def search_user(request):
    # 获取用户名
    user_name = request.POST.get('userName', None)
    # 去数据库查询
    try:
        user = models.User.objects.get(username=user_name)
        # 获取用户的角色
        roles = models.User2Role.objects.filter(user=user).values("role__id")
        # 检查有没有最高管理员
        for i in roles:
            # 如果有不能被搜索
            if i['role__id'] == 1:
                return HttpResponse('-1')
    except Exception:
        return HttpResponse('0')
    return HttpResponse(user.id)
