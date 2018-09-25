from io import BytesIO

from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse

from web.forms import registerForm, loginForm
from repository import models
from utils.check_code import create_validate_code
# 登陆注册页面展示


# 显示登陆注册页面
def show_page(request):
    # 实例化注册表单
    register_form = registerForm.RegisterForm()
    # 实例化登陆表单
    login_form = loginForm.LoginForm()
    return render(request, "login_register/login_register.html", {
        "register_obj": register_form,
        "login_obj": login_form,
    })


# 注册
def register(request):
    # 实例化注册表单
    register_form = registerForm.RegisterForm(request.session["check_code"], request.POST)
    # 实例化登陆表单
    login_form = loginForm.LoginForm()
    if register_form.is_valid():
        # 验证成功,将数据存入数据库
        data = register_form.cleaned_data
        try:
            models.User.objects.create(username=data['username'], pwd=data['pwd'], email=data['email'])
        except Exception:
            # 数据库插入数据异常，重新输入
            register_form.errors["__all__"] = "数据异常，请检查数据或稍后再试"
            return render(request, "login_register/login_register.html", {"register_obj": register_form})
        # 注册成功，到登陆页面
        return render(request, "login_register/success.html")
    return render(request, "login_register/login_register.html", {
        "register_obj": register_form,
        "login_obj": login_form,
    })


# 登陆
def login(request):
    # 实例化LoginForm对象
    login_form = loginForm.LoginForm(request.session["check_code"], request.POST)
    # 实例化注册对象
    register_form = registerForm.RegisterForm()
    if login_form.is_valid():
        # 验证成功, 将用户信息存入session
        data = login_form.cleaned_data
        user_obj = models.User.objects.get(username=data["username"], pwd=data["pwd"])
        try:
            path = user_obj.img.url
        except Exception:
            path = ""
        user = {
            'id': user_obj.id,
            "username": user_obj.username,
            "pwd": user_obj.pwd,
            "email": user_obj.email,
            "img": path
        }
        request.session["user"] = user
        # 做一个月免登陆
        if data["remenber_me"]:
            request.session.set_expiry(30*24*60*60)
        else:
            request.session.set_expiry(0)
        # 跳转到用户页面
        return redirect("/web/home.html-0")
    return render(request, "login_register/login_register.html", {
        "login_obj": login_form,
        "register_obj": register_form,
    })


# 登出
def logout(request):
    # 清除session
    del request.session["user"]
    request.session.clear()
    # 重定向到home
    path = reverse("home", kwargs={"category": 0})
    return redirect(path)


# 验证码
def check_code(request):
    f = BytesIO()          # 将图片暂时存放到内存里面
    img, code = create_validate_code()    # 生成图片跟验证码
    request.session["check_code"] = code    # 将验证码存入session中
    img.save(f, 'PNG')    # 将图片保存到内存中
    return HttpResponse(f.getvalue())   # 将内存中的图片返回给用户

