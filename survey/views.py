import time
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Avg      
from django.core.paginator import Paginator
from .models import Question as que
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


from .models import Survey, Response, Answer



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
        'query': query, # Add this
    }

    is_htmx = request.headers.get('HX-Request') == 'true'

    if is_htmx:
        return render(request, 'partials/Dashboard/table_with_oob_pagination.html', context)

    # For initial page loads, add any extra context needed.
    context['recent_surveys'] = survey_list[:4]
    return render(request, 'index.html', context)


def Responses(request, page_number=1):
    # البحث والفلترة
    search_query = request.GET.get('search', '').strip()
    survey_filter = request.GET.get('survey', '').strip()
    
    responses_list = Response.objects.select_related('survey', 'respondent').prefetch_related('answers')
    
    if search_query:
        responses_list = responses_list.filter(
            Q(respondent__username__icontains=search_query) |
            Q(survey__title__icontains=search_query)
        )
    
    if survey_filter:
        responses_list = responses_list.filter(survey_id=survey_filter)
    
    # الإحصائيات الأساسية
    total_responses = responses_list.count()
    
    # حساب مدة الاستبيان بالأيام
    if responses_list.exists():
        first_response = responses_list.order_by('created_at').first()
        survey_duration = (timezone.now() - first_response.created_at).days
        survey_start_date = first_response.created_at
    else:
        survey_duration = 0
        survey_start_date = timezone.now()
    
    # متوسط وقت الإجابة (مثال - تحتاج لتطوير)
    avg_response_time = "7.5"
            # التقسيم إلى صفحات
    paginator = Paginator(responses_list, 10)
    
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    surveys = Survey.objects.all()

    context = {
        'page': page,
        'total_responses': total_responses,
        'avg_response_time': avg_response_time,
        'survey_duration_days': survey_duration,
        'survey_start_date': survey_start_date,
        'surveys': surveys,
        'search_query': search_query,
        'selected_survey': survey_filter,
    }

    is_htmx = request.headers.get('HX-Request') == 'true'
    
    if is_htmx:
        return render(request, 'partials/Responses/responses_list.html', context)
    
    return render(request, 'Responses.html', context)


def ResponseDetail(request, response_id):
    """عرض تفاصيل رد معين"""
    response = get_object_or_404(Response, id=response_id)
    answers = response.answers.select_related('question')
    
    context = {
        'response': response,
        'answers': answers,
    }
    
    return render(request, 'partials/Responses/response_detail.html', context)

def CreateSurvey(request):
    context = {
                'question_library': que.get_available_type_names()  
    }
    return render(request, 'CreateSurvey.html', context)

# HTMX 
@require_POST
def DeleteSurvey(request, uuid):
    item = get_object_or_404(Survey, uuid=uuid)

    if item.created_by != request.user:
        return HttpResponse("Unauthorized", status=403)

    item.delete()
    return HttpResponse(status=200)

@require_POST
def DeleteResponse(request, response_id):
    """حذف رد معين"""
    response = get_object_or_404(Response, id=response_id)
    
    # تحقق من الصلاحيات (فقط منشئ الاستبيان يمكنه حذف الردود)
    if response.survey.created_by != request.user:
        return HttpResponse("Unauthorized", status=403)
    
    response.delete()
    return HttpResponse(status=200)


def CallTheModal(request):
    return render(request, 'partials/Modalfile.html')

def CreateFile(request):
    try:
        filename = request.POST.get('filename', '').strip()
        if not filename:
            return HttpResponse("Filename is required", status=400)
            
        context = {'filename': filename}
        return render(request, 'partials/subFile.html', context)
        
    except Exception as e:
        return HttpResponse("An error occurred", status=500)


