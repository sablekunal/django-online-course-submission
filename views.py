from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Course, Submission, Choice, Enrollment

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        # Get enrollment for user
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        submission = Submission.objects.create(enrollment=enrollment)
        for key, value in request.POST.items():
            if key.startswith('choice_'):
                choice_id = value
                choice = Choice.objects.get(pk=choice_id)
                submission.choices.add(choice)
        
        return HttpResponseRedirect(reverse('onlinecourse:show_exam_result', args=(course.id, submission.id,)))

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    score = 0
    questions = course.question_set.all()
    for question in questions:
        correct_choices = question.choice_set.filter(is_correct=True)
        selected_choices = submission.choices.filter(question=question)
        if set(correct_choices) == set(selected_choices):
            score += question.grade
            
    total_grade = sum(q.grade for q in questions)
    passed = score >= (total_grade * 0.7) if total_grade > 0 else False
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', {
        'course': course,
        'score': score,
        'passed': passed,
        'total_grade': total_grade
    })
