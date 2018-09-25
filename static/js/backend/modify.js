// 修改标签以及分类
function update(url){
    // 修改标签
    let editContent = null;
    $(".edit").click(edit);
    function edit(){
        // 获取标签id
        let nid = $(this).data('nid');
        // 获取当前标签对应的内容
        let tdDom = $(this).parent().parent().children().eq(0);
        let tdContent = tdDom.html();
        let value = tdDom.children().eq(0).html();
        // 将显示标签的a标签替换成input框
        let inputDom = document.createElement("input");
        inputDom.value = value;
        inputDom.type = 'text';
        tdDom.empty().append(inputDom);
        // 将删除按钮做成取消
        let cancelDom = $(this).prev();
        let deleteContent = cancelDom.html();
        cancelDom.empty();
        cancelDom.html(`
            <a href="javascript:void(0);" style="color: #fff;">
                <i class="glyphicon glyphicon-remove"></i>
                <span>取消</span>
            </a>
        `);
        // 给取消绑定事件
        let othis = $(this);
        $(cancelDom).click(function(){
            // 将标签caption还原
            tdDom.empty().html(tdContent);
            // 将取消按钮还原
            $(this).empty().html(deleteContent);
            othis.empty().html(editContent);
            // 恢复绑定事件
            othis.unbind('click');
            othis.click(edit);
        });

        // 将编辑按钮做成修改
        editContent = $(this).html();
        $(this).empty();
        $(this).html(`
            <i class="glyphicon glyphicon-leaf"></i>
            <a href="javascript:void(0);" style="color: #fff;">修改</a>
        `);
        // 重新绑定当前span标签点击事件
        $(this).unbind('click');
        $(this).click(modify.bind(tdDom, nid, value));
    }

    function modify(nid, value){
        // 重新获取标签名
        let tagName = $(this).children().val();
        // 如果标签名已经改变而且不等于空就发送ajax请求。否则刷新页面
        if((tagName.trim() !== value) && (tagName.trim() !== '')){
            $.ajax({
                url: url,
                type: 'post',
                data: {'tagId': nid, 'caption': tagName.trim()},
                success (data){
                    if(data === '0'){
                        alert('去你娘的，别乱搞');
                    }else{
                        alert('修改成功');
                    }
                    window.location.reload();
                }
            });
        }else{
            window.location.reload();
        }
    }
}


// 搜索功能
function search(url){
    // 获取value值去后台查询
    let value = $(this).val();
    // 发送到后台
    $.ajax({
        url: url,
        type: 'post',
        data: {'value': value},
        success (args){
            $(".page-nation").html(args);
        }
    });
}


