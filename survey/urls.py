from django.urls import include, path
from . import views

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('Dashboard', views.Index, name='Dashboard'),
    path('Dashboard/<int:page_number>', views.Index, name='Dashboard_Page'),
    path('CreateSurvey', views.CreateSurvey, name='CreateSurvey'),
    
    # Responses URLs
    path('responses', views.Responses, name='Responses'),
    path('responses/<int:page_number>', views.Responses, name='Responses_Page'),
    path('responses/survey/<uuid:uuid>', views.SurveyResponseDetail, name='SurveyResponseDetail'),
    path('responses/survey/<uuid:uuid>/analytics', views.SurveyAnalytics, name='SurveyAnalytics'),
    
    # API endpoint for chart data
    path('api/survey/<uuid:uuid>/question/<int:question_id>/chart-data', views.GetChartData, name='GetChartData'),
]

url_for_htmx = [
    path('CreateSubFile', views.CreateFile, name='CreateSubFile'),
    path("surveys/<uuid:uuid>/delete", views.DeleteSurvey, name="DeleteSurvey"),
]

urlpatterns += url_for_htmx