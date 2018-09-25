# 分页处理
class Pagenation(object):
    def __init__(self, total_count, current_page, perpage_count=10, max_page_num=5, url='javascript:void(0);'):
        self.totalCount = total_count
        pre_max_page = total_count // perpage_count
        self.max_page = pre_max_page if (total_count % perpage_count == 0) else (pre_max_page + 1)
        try:
            current = int(current_page)
            self.current_page = current if current > 0 else 1
            # 判断索引是否超过了最大页数,前提是最大页不为0
            if self.max_page > 0:
                self.current_page = self.max_page if current > self.max_page else current
        except Exception:
            self.current_page = 1
        self.perpage_count = perpage_count
        self.max_page_num = max_page_num
        self.url = url

    @property
    def start_index(self):        # 起始索引
        # 起始索引 = (当前页 - 1) * 每页显示的数据条数
        return (self.current_page - 1) * self.perpage_count

    @property
    def end_index(self):          # 结束索引
        # 结束索引 = 当前页 * 每一页显示的数据条数
        return self.current_page * self.perpage_count

    def page_nation(self):    # 页面展示
        # 更新max_page_num
        self.max_page_num = self.max_page_num if self.max_page >= self.max_page_num else self.max_page
        # 计算分页按钮的起始数字
        current_minus_max_page = self.current_page - (self.max_page_num // 2)
        current_add_max_page = self.current_page + (self.max_page_num // 2)
        if current_minus_max_page <= 0:
            # 还能够展示第一页
            result = range(1, self.max_page_num + 1)
        elif current_minus_max_page > 0 and current_add_max_page < self.max_page:
            # 不能够展示第一页而且还不到最后一页的附近
            start = self.current_page - self.max_page_num // 2
            result = range(start, self.max_page_num + start)
        else:
            # 到了最后一页附近
            result = range(self.max_page - self.max_page_num + 1, self.max_page + 1)
        return result

    @property
    def previous_page(self):      # 上一页
        return self.current_page - 1 if self.current_page > 1 else 1

    @property
    def next_page(self):       # 下一页
        return self.current_page + 1 if self.current_page < self.max_page else self.max_page

