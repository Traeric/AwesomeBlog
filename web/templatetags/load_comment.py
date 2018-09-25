from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def load_comment(child_comment):
    """
    使用递归加载子评论
    :return:
    """
    content = ''
    if not child_comment:   # 如果什么都没有就不执行
        return ''
    for comment in child_comment:
        content += """
        <div class="return-comment" 
        style="position: relative; background-color: #efefef; 
        border-bottom: 1px solid #dedede; border-left: 2px solid #dedede; margin-left: 20px;">
            <div class="c-comment">
                <div class="c-person"><a href="javascript:void(0);">%s</a>
                <span>%s</span>
                </div>
                <div class="content">%s</div>
                <!-- 在这里加载子评论 -->
                %s
            </div>
            <div class="return re-comment" data-nid="%s" data-user="%s" style="position: absolute; top: 0; right: 20px;">
                <a href="javascript:void(0);">回复</a>
            </div>
        </div>
        """ % (comment['user'].username,
               comment['ctime'],
               mark_safe(comment['content']),
               load_comment(comment['child']),      # 添加子评论
               comment['id'], comment['user'].username)

    return mark_safe(content)




