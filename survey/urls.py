from django.urls import include, path
from . import views

# app_name = "survey" 

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('Dashboard', views.Index, name='Dashboard'),
    path('Dashboard/<int:page_number>', views.Index, name='Dashboard_Page'),
    # the views need to be Change
    path('CreateSurvey', views.CreateSurvey, name='CreateSurvey'),
    path('responses/', views.responses_index, name='Responses'),
    path('surveys/<int:survey_id>/responses/', views.survey_responses, name='survey_responses'),

]

url_for_htmx = [
    path('CreateSubFile', views.CreateFile, name='CreateSubFile'),
    path("surveys/<uuid:uuid>/delete", views.DeleteSurvey, name="DeleteSurvey"),
    # path('SearchSurveys', views.SearchSurveys, name='SearchSurveys'),
    path("responses/<int:response_id>/detail", views.ResponseDetail, name="ResponseDetail"),
    path("responses/<int:response_id>/delete", views.DeleteResponse, name="DeleteResponse"),


]

urlpatterns += url_for_htmx
print(urlpatterns)