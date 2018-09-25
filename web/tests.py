from django.test import TestCase

# Create your tests here.

print(bool(''))
string = 'sdddddd{[]}dnjsnd'

print("""
                <div class="re-comment" style="position: relative; background-color: #efefef; border-bottom: 1px solid #dedede;">
                    <div class="c-comment" style="margin-left: 20px;">
                        <div class="c-person"><a href="javascript:void(0);">%s</a>
                        <span>%s</span>
                        </div>
                        <div class="content">%s</div>
                        <!-- 在这里加载子评论 -->
                        @#@#@#@
                    </div>
                    <div class="return re-comment" data-nid="%s" data-user="%s" style="position: absolute; top: 0; right: 20px;">
                        <a href="javascript:void(0);">回复</a>
                    </div>
                </div>
                """.replace('@#@#@#@', 'fgklsdljsdlfjl'))


