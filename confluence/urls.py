# urls.py
from django.urls import path
from .views import modify_content, confluence_space_info, step_1, step_2, step_3, index, update_confluence_content

urlpatterns = [
    path('', index, name='index'),
    path('modify/', modify_content, name='modify_content'),
    path('confluence_space_info/', confluence_space_info, name='confluence_space_info'),
    path('step1/', step_1, name='step1'),
    path('step2/', step_2, name='step2'),
    path('step3/', step_3, name='step3'),
    # path('update_confluence_content/', update_confluence_content, name='update_confluence_content'),
    path('update_confluence_content/', update_confluence_content, name='update_confluence_content'),
]
