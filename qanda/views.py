import json
from django.http import HttpResponse
import requests
from django.shortcuts import render
from django.http import JsonResponse
from qanda.models import QandAModel
import random


def index(request):
    original_subjects = {
        "0": "english",
        "1": "mathematics",
        "2": "commerce",
        "3": "accounting",
        "4": "biology",
        "5": "physics",
        "6": "chemistry",
        "7": "englishlit",
        "8": "government",
        "9": "crk",
        "10": "geography",
        "11": "economics",
        "12": "irk",
        "13": "civiledu",
        "14": "insurance",
        "15": "currentaffairs",
        "16": "history"
    }

    subjects = list(original_subjects.values())
    all_responses = []
    for subject in subjects:
        existing_questions = QandAModel.objects.filter(subject=subject)
        count = existing_questions.count()
        response_text = f"""<div>Number of existing {
            subject} questions: {count}</div>"""
        all_responses.append(response_text)

    return HttpResponse('\n'.join(all_responses))


def get_all_subjects(request):
    original_subjects = {
        "0": "english",
        "1": "mathematics",
        "2": "commerce",
        "3": "accounting",
        "4": "biology",
        "5": "physics",
        "6": "chemistry",
        "7": "englishlit",
        "8": "government",
        "9": "crk",
        "10": "geography",
        "11": "economics",
        "12": "irk",
        "13": "civiledu",
        "14": "insurance",
        "15": "currentaffairs",
        "16": "history"
    }
    subjects = list(original_subjects.values())
    random.shuffle(subjects)
    # Get parameters
    q_type = request.GET.get('type', 'utme')

    # Define constants
    BASE_URL = "https://questions.aloc.com.ng/api/v2/q/40"
    ACCESS_TOKEN = "ALOC-93ed3dd5c8d940d9c650"

    # Create headers
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Accept': 'application/json',
        'AccessToken': ACCESS_TOKEN
    }
    try:
        for subject in subjects:
            print(subject)
            api_url = f"{BASE_URL}?subject={subject}&type={q_type}"

            # Make request
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()

            # Extract data
            data = response.json()

            if len(data['data']) > 0:
                for question_data in data['data']:
                    existing_question = QandAModel.objects.filter(
                        source_id=question_data['question']).first()
                    if existing_question is None:
                        QandAModel.objects.create(
                            question=question_data['question'],
                            subject=data['subject'],
                            source_id=question_data['id'],
                            options=question_data['option'],
                            section=question_data['section'],
                            image=question_data['image'],
                            answer=question_data['answer'],
                            solution=question_data['solution'],
                            examtype=question_data['examtype'],
                            examyear=question_data['examyear']
                        )

        # Move the return statement outside the loop
        return JsonResponse("processed", json_dumps_params={'indent': 2})

    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "error fetching data": str(e)
        }, status=500)


def fetch_q_and_a(request):

    # Get parameters
    subject = request.GET.get('subject')
    q_type = request.GET.get('type')

    # Define constants

    # BASE_URL =  config['API_BASE_URL']
    # ACCESS_TOKEN = config['SECRET_KEY']
    BASE_URL = "https://questions.aloc.com.ng/api/v2/q/40"
    ACCESS_TOKEN = "ALOC-93ed3dd5c8d940d9c650"

    # Build URL
    api_url = f"{BASE_URL}?subject={subject}&type={q_type}"

    # Create headers
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Accept': 'application/json',
        'AccessToken': ACCESS_TOKEN
    }

    try:
        # Make request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        # Extract data
        data = response.json()

        if (len(data['data']) > 0):
            for question_data in data['data']:
                existing_question = QandAModel.objects.filter(
                    source_id=question_data['question']).first()
                if existing_question is None:
                    QandAModel.objects.create(
                        question=question_data['question'],
                        subject=data['subject'],
                        source_id=question_data['id'],
                        options=question_data['option'],
                        section=question_data['section'],
                        image=question_data['image'],
                        answer=question_data['answer'],
                        solution=question_data['solution'],
                        examtype=question_data['examtype'],
                        examyear=question_data['examyear']
                    )

            return JsonResponse(data, json_dumps_params={'indent': 2})

    except requests.exceptions.RequestException as e:

        return JsonResponse({
            "error": str(e)
        }, status=500)


def view_q_and_a(request):
    # Get parameters
    subject = request.GET.get('subject').lower()
    q_type = request.GET.get('type').lower()
    limit = request.GET.get('limit', 100)

    try:
        existing_questions = QandAModel.objects.filter(
            subject=subject, examtype=q_type
        ).order_by('?')[:int(limit)]

        count = existing_questions.count()
        info = "here are the result"
        if count == 0:
            existing_questions = QandAModel.objects.filter(
                subject=subject
            ).order_by('?')[:int(limit)]
        count = existing_questions.count()
        info = f"we could not find one for {
            q_type} so we matched and fetched others"
        # Create a list to store the results
        result_data = []

        for question in existing_questions:
            # Add existing questions to the result_data list
            result_data.append({
                'question': question.question,
                'subject': question.subject,
                'id': str(question.id),
                'options': question.options,
                'section': question.section,
                'image': question.image,
                'answer': question.answer,
                'solution': question.solution,
                'examtype': question.examtype,
                'examyear': question.examyear
            })

        return JsonResponse({'count': count, 'info': info, 'data': result_data}, json_dumps_params={'indent': 2})

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)
