import re

from django.http import HttpResponse
from repository import models


class MenuCreater(object):
    def __init__(self, request, nid):
        # 获取当前请求的request对象
        self.request = request
        # 获取当前的用户id
        self.id = nid
        # 获取当前的URL
        self.current_url = request.path_info

        # 获取当前用户的所有权限
        self.permission2action_dict = None
        # 获取在菜单中展示的URL
        self.url_in_menu = None
        # 获取所有的菜单
        self.menu_list = None
        # 初始化这些数据
        self.init_data()

    def init_data(self):
        """
        初始化数据，将数据从session中取出然后赋值，如果session中没有数据，
        那么进行取值然后存到session中
        :return:
        """
        # 从session中获取数据
        permission_dict = self.request.session.get('permission_info', None)
        if permission_dict:
            # 如果session中已经有数据了，直接赋值
            self.permission2action_dict = permission_dict['permission2action_dict']
            self.url_in_menu = permission_dict['url_in_menu']
            self.menu_list = permission_dict['menu_list']
        else:
            # 否则，是第一次获取
            # 获取该用户所有的角色
            role_list = models.Role.objects.filter(user2role__user__id=self.id)

            # 通过所有的角色确定该用户的所有权限  （URL + Action）
            permission2action_list = (
                models.Permission2Action.objects.filter(permission2action2role__role__in=role_list).
                values("permission__url", "action__code"))
            permission2action_dict = {}
            for item in permission2action_list:
                if item['permission__url'] in permission2action_dict.keys():
                    permission2action_dict[item['permission__url']].append(item['action__code'])
                else:
                    permission2action_dict[item['permission__url']] = [item['action__code'], ]

            # 获取应该在菜单栏中展示的URL，即permission
            url_in_menu = (list(models.Permission2Action.objects.filter(permission2action2role__role__in=role_list).
                           exclude(permission__menu__isnull=True).  # 去掉没有跟菜单绑定的URL
                           values('permission__id', 'permission__url', 'permission__caption',
                                  'permission__menu').distinct()))

            # 获取所有的Menu
            menu_list = list(models.Menu.objects.values('id', 'caption', 'parent'))

            # 将数据封装到session中
            self.request.session['permission_info'] = {
                'permission2action_dict': permission2action_dict,
                'url_in_menu': url_in_menu,
                'menu_list': menu_list
            }
            self.init_data()

    def process_data(self):
        """
        处理初始化后的数据，得到一个树形的菜单结构，将URL挂载到相应的菜单底下
        :return:
        """
        open_url_parent_id = 0
        # 将URL的列表转换成字典，而且以它们对应的menu的id作为键
        url_in_menu_dict = {}
        for item in self.url_in_menu:
            item = {
                'id': item['permission__id'],
                'url': item['permission__url'],
                'caption': item['permission__caption'],
                'parent_id': item['permission__menu'],
                'status': True,   # 是否显示
                'open': False     # 是否被打开
            }
            if item['parent_id'] in url_in_menu_dict.keys():  # 如果已经有了这个key，也就是两个URL在同一菜单下
                url_in_menu_dict[item['parent_id']].append(item)
            else:
                url_in_menu_dict[item['parent_id']] = [item, ]
            # 判断当前打开的URL
            if re.match(item['url'], self.current_url):
                item['open'] = True
                open_url_parent_id = item['parent_id']    # 获取到打开URL的父菜单id

        # 将所有菜单用字典储存起来，以id作为键
        menu_dict = {}
        for item in self.menu_list:
            item['child'] = []
            item['status'] = False
            item['open'] = False
            menu_dict[item['id']] = item

        # 把URL挂到相应的菜单底下
        for k, v in url_in_menu_dict.items():
            menu_dict[k]['child'] = v
            parent_id = k
            # 将包裹了URL的菜单标记为显示，展示给用户看
            while parent_id:
                menu_dict[parent_id]['status'] = True
                parent_id = menu_dict[parent_id]['parent']

        # 将已经选中的菜单标记为展开
        while open_url_parent_id:
            menu_dict[open_url_parent_id]['open'] = True
            open_url_parent_id = menu_dict[open_url_parent_id]['parent']

        # 将菜单字典中有parend_id的菜单项都放到其对应的菜单下面
        result = []
        for item in menu_dict.values():
            if not item['parent']:
                result.append(item)
            else:
                menu_dict[item['parent']]['child'].append(item)

        return result

    def menu_tree(self):
        """
        加载第一层的菜单
        :return:
        """
        result_str = ''
        tpl = """
            <li class="sub-menu knowledge">
                <a href="javascript:void(0);" class="one">
                    <i class="fa fa-desktop"></i>
                    <span>%s</span>
                </a>
                <ul class="sub">
                    %s
                </ul>
            </li>
        """
        # 处理树形数据
        for row in self.process_data():
            # 只加载显示了的
            if not row['status']:
                continue
            # 第一层菜单
            title = row['caption']
            # 处理第一层的后代
            content = self.menu_child(row['child'])
            result_str += tpl % (title, content)
        return result_str

    def menu_child(self, lists):
        result_str = ""
        tpl = """
            <li>
                <a href="javascript:void(0);" class="one">
                    <i class="fa fa-desktop"></i>
                    <span>%s</span>
                </a>
                <ul class="sub">
                    %s
                </ul>
            </li>
        """
        for row in lists:
            if not row['status']:
                continue
            if 'url' in row:
                result_str += "<li><a href='%s'>%s</a></li>" % (row['url'].replace('\d+', '0'), row['caption'])
            else:
                title = row['caption']
                content = self.menu_child(row['child'])
                result_str += tpl % (title, content)
        return result_str

    def is_permission(self):
        """
        检查当前用户是否能访问当前的URL，如果可以，返回该用户能在当前URL下做的操作
        :return:
        """
        action_list = []
        # 获取用户的所有权限
        for k, v in self.permission2action_dict.items():
            if re.match(k, self.current_url):
                action_list = v
                break
        return action_list


# 装饰器，添加到相应的视图函数上可以判断用户是否具有相应的权限
def permission(func):
    def inner(request, *args, **kwargs):
        user_id = request.session['user'].get('id')
        obj = MenuCreater(request, user_id)
        action_list = obj.is_permission()
        if not action_list:
            return HttpResponse("抱歉，无权访问")
        kwargs['menu_string'] = obj.menu_tree()
        kwargs['action_list'] = action_list
        return func(request, *args, **kwargs)
    return inner



