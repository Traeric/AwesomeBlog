from django.conf.urls import url
from backend.views import knowledge
from backend.views import trouble


urlpatterns = [
    url(r"^index.html$", knowledge.index, name="index"),
    url(r"^article.html-(?P<main_stack>\d+)-(?P<category>\d+)$", knowledge.article, name="article"),
    url(r"^article_page_nation", knowledge.article_page_nation, name="article_page_nation"),
    url(r'^search_article$', knowledge.search_article, name="search_article"),
    url(r'^add_article$', knowledge.add_article, name="add_article"),
    url(r'^modify_article-(?P<article_id>\d+)$', knowledge.modify_article, name="modify_article"),
    url(r'^category.html$', knowledge.category, name="category"),
    url(r'^add_category$', knowledge.add_category, name="add_category"),
    url(r'^delete_category$', knowledge.delete_category, name="delete_category"),
    url(r'^modify_category$', knowledge.modify_category, name="modify_category"),
    url(r'^tag.html$', knowledge.tag, name='tag'),
    url(r'^add_tag$', knowledge.add_tag, name="add_tag"),
    url(r'^delete_tag$', knowledge.delete_tag, name="delete_tag"),
    url(r'^modify_tag$', knowledge.modify_tag, name="modify_tag"),
    url(r'^personnel_info$', knowledge.personnel, name='personnel'),
    url(r'^modify_personnel$', knowledge.modify_personnel, name="modify_personnel"),
    url(r'^set_header_img$', knowledge.set_header, name="set_header"),
    url(r'^display_trouble_list$', trouble.display_trouble_list, name="display_trouble_list"),
    url(r'^display_trouble_page_nation$', trouble.display_trouble_page_nation, name='display_pagenation'),
    url(r"^create_trouble_list$", trouble.create_trouble_list, name="create_trouble_list"),
    url(r"^save_trouble_list$", trouble.save_trouble_list, name="save_trouble_list"),
    url(r'^search_trouble_list$', trouble.search_trouble_list, name="search_trouble_list"),
    url(r"^display_handle_trouble_list$", trouble.display_handle_trouble_list, name="display_handle_trouble_list"),
    url(r'^handle_trouble_page_nation$', trouble.handle_trouble_page_nation, name="handle_trouble_page_nation"),
    url(r"^get_trouble_list$", trouble.get_trouble_list, name="get_trouble_list"),
    url(r"^handle_trouble_list$", trouble.handle_trouble_list, name="handle_trouble_list"),
    url(r"^save_solve_plan$", trouble.save_solve_plan, name="save_solve_plan"),
    url(r"^watch_solve_plan$", trouble.watch_solve_plan, name="watch_solve_plan"),
    url(r'^evaluate$', trouble.evaluate, name="evaluate"),
    url(r'^search_handle_trouble$', trouble.search_handle_trouble, name="search_handle_trouble"),
    url(r'^draw_trouble$', trouble.draw_trouble, name="draw_trouble"),
    url(r'^get_data$', trouble.get_data, name="get_data"),
    url(r'^giving_action$', trouble.giving_action, name="giving_action"),
    url(r'^save_role$', trouble.save_role, name="save_role"),
    url(r'^search_user.html$', trouble.search_user, name="search_user"),
]


