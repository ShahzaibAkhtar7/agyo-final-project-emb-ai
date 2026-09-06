from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .models import Course, Lesson, Question, Choice, Submission, Enrollment

class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list.html'
    context_object_name = 'course_list'
    def get_queryset(self):
        return Course.objects.order_by('-pub_date')[:5]

class CourseDetailsView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail.html'

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
    if request.method == 'POST':
        selected_ids = request.POST.getlist('choice')
        submission = Submission.objects.create(enrollment=enrollment)
        for choice_id in selected_ids:
            choice = Choice.objects.get(pk=choice_id)
            submission.choices.add(choice)
        submission.save()
        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    total_score = 0
    selected_ids = [choice.id for choice in submission.choices.all()]
    for question in course.question_set.all():
        total_score += question.grade if question.is_get_score(selected_ids) else 0
    context['course'] = course
    context['grade'] = total_score
    context['submission'] = submission
    return render(request, 'onlinecourse/exam_result.html', context)
