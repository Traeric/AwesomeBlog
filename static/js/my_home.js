var article = $(".article");
article.each(function(index, item){
    if(index !== article.length - 1){
        $(item).css("border-bottom", "none");
    }
});
// 鼠标进入文章区域后边框变色
var temp = null;
$(article).mouseover(function(){
    $(this).css({
        "border-top-color": "#169fe6",
        "border-left-color": "#169fe6",
        "border-right-color": "#169fe6",
    });
    var othis = this;
    // 如果该篇文章是第一篇，将下一篇文章的顶部也变颜色，否则将上一篇文章的底部变颜色
    $(article).each(function(index, item){
        if((othis === item) && (index !== article.length - 1)){
            $(article).eq(index + 1).css("border-top-color", "#169fe6");
            temp = $(article).eq(index + 1);
        }
    });
});
// 鼠标移出后恢复
$(article).mouseout(function(){
    $(this).css({
        "border-top-color": "#dedede",
        "border-left-color": "#dedede",
        "border-right-color": "#dedede",
    });
    $(temp).css("border-top-color", "#dedede");
});


// 富文本
KindEditor.ready(function(K){
    editor = K.create(
        "#comment",
        {
            resizeType: 0,
            allowPreviewEmoticons: true,
            width: '100%',
            height: '200px',
            items: [
                'source', '|', 'undo', 'redo', '|', 'preview', 'print', 'code', 'cut', 'copy', 'paste',
                '|', 'bold', 'italic', 'underline', 'strikethrough', 'emoticons', '|', 'link', 'unlink',
                'removeformat'
            ]
        }
    );
});



