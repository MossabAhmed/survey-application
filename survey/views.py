import time
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from .models import Question as que, Survey, Response, Answer, MultiChoiceQuestion, LikertQuestion
import json


def Index(request, page_number=1):
    query = request.GET.get('search', '').strip()

    if query:
        survey_list = Survey.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).order_by('-last_updated')
    else:
        survey_list = Survey.objects.order_by('-last_updated')

    paginator = Paginator(survey_list, 5)
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'query': query,
        'is_responses_page': False, # Explicitly set for Dashboard
    }

    is_htmx = request.headers.get('HX-Request') == 'true'

    if is_htmx:
        return render(request, 'partials/Dashboard/table_with_oob_pagination.html', context)

    context['recent_surveys'] = survey_list[:4]
    return render(request, 'index.html', context)


def Responses(request, page_number=1):
    """Main responses view showing all surveys with response counts"""
    query = request.GET.get('search', '').strip()
    
    # Get surveys with response counts
    surveys = Survey.objects.annotate(
        responses_count=Count('responses')
    ).filter(state='published')
    
    if query:
        surveys = surveys.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    
    surveys = surveys.order_by('-last_updated')
    
    # Get recent surveys with responses
    recent_surveys_with_responses = surveys.filter(responses_count__gt=0)[:10]
    
    # Pagination
    paginator = Paginator(surveys, 10)
    page = paginator.get_page(page_number)
    
    context = {
        'page': page,
        'query': query,
        'recent_surveys': recent_surveys_with_responses,
        'is_responses_page': True, # Added for sidebar consistency
    }
    
    is_htmx = request.headers.get('HX-Request') == 'true'
    
    if is_htmx:
        return render(request, 'partials/Responses/responses_table_body.html', context)
    
    return render(request, 'Responses.html', context)


def SurveyResponseDetail(request, uuid):
    """Detailed view of responses for a specific survey"""
    survey = get_object_or_404(Survey, uuid=uuid)
    responses = Response.objects.filter(survey=survey).order_by('-created_at')
    
    # Pagination for responses
    page_number = request.GET.get('page', 1)
    paginator = Paginator(responses, 20)
    page = paginator.get_page(page_number)
    
    # Get statistics
    total_responses = responses.count()
    
    context = {
        'survey': survey,
        'responses': page,
        'total_responses': total_responses,
        'page': page,
    }
    
    return render(request, 'SurveyResponseDetail.html', context)


def SurveyAnalytics(request, uuid):
    """Analytics and charts for a specific survey"""
    survey = get_object_or_404(Survey, uuid=uuid)
    questions = survey.questions.all()
    
    # Prepare analytics data for each question
    analytics_data = []
    
    for question in questions:
        question_data = {
            'question': question,
            'type': type(question).__name__,
        }
        
        if isinstance(question, MultiChoiceQuestion):
            # Get distribution for multiple choice
            mc_question = MultiChoiceQuestion.objects.get(pk=question.pk)
            distribution = mc_question.get_answer_distribution()
            question_data['distribution'] = distribution
            question_data['chart_type'] = 'bar'
            
        elif isinstance(question, LikertQuestion):
            # Get rating distribution and average
            likert_question = LikertQuestion.objects.get(pk=question.pk)
            distribution = likert_question.get_rating_distribution()
            average = likert_question.get_average_rating()
            question_data['distribution'] = distribution
            question_data['average'] = average
            question_data['chart_type'] = 'bar'
        
        analytics_data.append(question_data)
    
    context = {
        'survey': survey,
        'analytics_data': analytics_data,
        'total_responses': survey.response_count,
    }
    
    return render(request, 'SurveyAnalytics.html', context)


def GetChartData(request, uuid, question_id):
    """API endpoint to get chart data for a specific question"""
    survey = get_object_or_404(Survey, uuid=uuid)
    question = get_object_or_404(que, pk=question_id)
    
    data = {
        'labels': [],
        'values': [],
        'question_label': question.label,
    }
    
    if isinstance(question, MultiChoiceQuestion):
        mc_question = MultiChoiceQuestion.objects.get(pk=question.pk)
        distribution = mc_question.get_answer_distribution()
        data['labels'] = list(distribution.keys())
        data['values'] = list(distribution.values())
        
    elif isinstance(question, LikertQuestion):
        likert_question = LikertQuestion.objects.get(pk=question.pk)
        distribution = likert_question.get_rating_distribution()
        data['labels'] = [str(k) for k in distribution.keys()]
        data['values'] = list(distribution.values())
        data['average'] = likert_question.get_average_rating()
    
    return JsonResponse(data)


def CreateSurvey(request):
    context = {
        'question_library': que.get_available_type_names()  
    }
    return render(request, 'CreateSurvey.html', context)


# HTMX 
@require_POST
def DeleteSurvey(request, uuid):
    item = get_object_or_404(Survey, uuid=uuid)
    item.delete()
    return HttpResponse(status=200)


def CallTheModal(request):
    return render(request, 'partials/Modalfile.html')


def CreateFile(request):
    filename = request.POST.get('filename')
    context = {'filename': filename}
    return render(request, 'partials/subFile.html', context)