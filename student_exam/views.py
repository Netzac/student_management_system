import os
import json
import datetime
from re import template
from uuid import uuid4
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector, SearchQuery
# Create your views here.

from student_exam import forms
from student_exam.models import Assignment, Submission,Gradebook, OverallGradebook

'''is_ajax deprecated so define a custom function'''

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH')=='XMLHttpRequest'

@login_required
def dashboard(request):
    assignment_form = forms.AssignmentForm(request.POST or None)
    search_form = forms.AssignmentSearchForm(request.GET or None)
    user_id = request.user.id
    user = request.user
    assignments = request.user.assignments.get_queryset().order_by('id')
    
    assignments_list = assignments
    if user.user_type == '1':
        template_name ='student_exam/dashboard.html'
        paginator = Paginator(assignments_list, 10)
        page = request.GET.get('page')
        try:
            assignments_list = paginator.page(page)
        except PageNotAnInteger:
            assignments_list = paginator.page(1)
        except EmptyPage:
            assignments_list = paginator.page(paginator.num_pages)

       
        if request.method == 'GET':
            if search_form.is_valid():
                q = request.GET['q']
                assignments = assignments.annotate(
                    search=SearchVector('title', 'course', 'title'),
                    ).filter(search=SearchQuery(q))

                paginator = Paginator(assignments, 10)
                page = request.GET.get('page')
                try:
                    assignments = paginator.page(page)
                except PageNotAnInteger:
                    assignments = paginator.page(1)
                except EmptyPage:
                    assignments = paginator.page(paginator.num_pages)
            else:
                for error in search_form.errors.values():
                    messages(request, error)
                   
                context = {
                    "assignments": assignments,
                    "search_form": search_form,
                    "assignment": assignment_form
                }
                return render(request, template_name, context=context)
               
        context = {
            "assignments": assignments,
            "assignment": assignment_form,
            "search_form": search_form
        }
        return render(request, template_name, context=context)
    elif user.user_type == '3':
        template_name ='student_exam/students_dashboard.html'
        clsid = user.students.course_id_id
        print('Class id :', clsid)
       
        submissions = request.user.submissions.get_queryset().order_by('id')
        qSub = submissions.values('id')
        assignments = Assignment.objects.filter(course_id=clsid).exclude(id__in = qSub)
        print(qSub) 
        submissions_list = submissions
        search_form = forms.SubmissionSearchForm(request.GET or None)
        paginator = Paginator(submissions_list, 10)
        page = request.GET.get('page')
        try:
            submissions_list = paginator.page(page)
        except PageNotAnInteger:
            submissions_list = paginator.page(1)
        except EmptyPage:
            submissions_list = paginator.page(paginator.num_pages)

        if request.method == 'GET':
            if search_form.is_valid():
                q = request.GET['q']
                submissions = submissions.annotate(
                    search=SearchVector('matric_number'),
                    ).filter(search=SearchQuery(q))

                paginator = Paginator(submissions, 10)
                page = request.GET.get('page')
                try:
                    submissions = paginator.page(page)
                except PageNotAnInteger:
                    submissions = paginator.page(1)
                except EmptyPage:
                    submissions = paginator.page(paginator.num_pages)

                context = {
                    "assignments":assignments,
                    "search_form": search_form,
                    "submissions": submissions
                    }
                return render(request, template_name, context=context)
        context = {
            "search_form": search_form,
            "assignments":assignments,
            "submissions": submissions,
        }
        return render(request, template_name, context=context)



@login_required
def create_assignment(request):

    if is_ajax(request=request):
        template_name =  "student_exam/create_assignment_inner.html"
    else:
        template_name =  "student_exam/dashboard.html"
    # if request.user.profile.role == 'Lecturer':
    if request.method == "POST":
        assignment_form = forms.AssignmentForm(request.POST,request.FILES)
        
        if assignment_form.is_valid():
            assignment = assignment_form.save(commit=False)
            assignment.user_id = request.user.id
            print('User is :',request.user.id)
            assignment.save()
            new_data = Assignment.objects.last()
            messages.success(request, 'Assignment was successfully created.')
            return redirect('dashboard')
        else:
            for error in assignment_form.errors.values():
                messages.error(request, error)
    assignment_form = forms.AssignmentForm()
    context = {
        "assignment": assignment_form
    }
    return render(request, template_name, context=context)
    # else:
    #     messages.error(request, 'Only Lecturer accounts can create assignments')
    #     context = {
    #         "assignment": assignment_form
    #     }
        # return render(request, "ams_app/dashboard.html", context=context)




@login_required
def assignment_submissions(request, id):
    
    if is_ajax(request=request) and request.method == 'GET':
        template_name =  "student_exam/submissions_inner.html"
        grade_form = forms.GradeForm()
        context= {'grade_form':grade_form,'submission_id': id}
        return render(request, template_name, context=context)
    else:
        assignment_id = id
        template_name =  "student_exam/assignment_submissions.html"
        # assignment = Submission.objects.select_related('assignment').get(id=id)
    if request.user.user_type == '1':
        search_form = forms.SubmissionSearchForm(request.GET or None)
        feedback_form = forms.FeedbackForm(request.POST or None)
        grade_form = forms.GradeForm(request.POST or None)
        try:
            assignment = Assignment.objects.get(id=assignment_id)
            submissions = assignment.submissions.all().order_by('matric_number')
            submissions_list = submissions
            paginator = Paginator(submissions_list, 10)
            page = request.GET.get('page')
            try:
                submissions_list = paginator.page(page)
            except PageNotAnInteger:
                submissions_list = paginator.page(1)
            except EmptyPage:
                submissions_list = paginator.page(paginator.num_pages)

        except Assignment.DoesNotExist:
            assignment = None
            submissions = None
            submissions_list=None
            paginator= None
       
        
       
        if request.method == 'POST':
            # if feedback_form.is_valid():
            #     feedback = request.POST['feedback']
            #     submission_id = request.POST['submit-feedback']
            #     submission = Submission.objects.get(id=submission_id)
            #     submission.feedback = feedback
            #     submission.save()
            if grade_form.is_valid():
                grade = request.POST['grade']
                submission_id = request.POST['submit-grade']
                feedback = request.POST['feedback']
                submission = Submission.objects.get(id=submission_id)
                submission.grade = grade
                submission.feedback =feedback
                submission.save()
                return redirect('submissions', id=submission.assignment.id)
        if request.method == "GET":
            if search_form.is_valid():
                q = request.GET['q']
                submissions = submissions.annotate(
                    search=SearchVector('matric_number'),
                    ).filter(search=SearchQuery(q))

                paginator = Paginator(submissions, 10)
                page = request.GET.get('page')
                try:
                    submissions = paginator.page(page)
                except PageNotAnInteger:
                    submissions = paginator.page(1)
                except EmptyPage:
                    submissions = paginator.page(paginator.num_pages)

                context = {
                    "search_form": search_form,
                    "submissions": submissions
                }
                return render(request, template_name, context=context)

        context = {
                "search_form": search_form,
                "submissions": submissions,
                "grade_form": grade_form,
                "feedback_form": feedback_form,
                "assignment_id": assignment_id
            }
        return render(request,template_name, context=context)



@login_required
def assignment_detail(request, id):
    assignment = Assignment.objects.get(id=id)
    initial = {
        "title": assignment.title,
        "content": assignment.content,
        "upload": assignment.upload,
        "due_date": assignment.due_date,
        "Class": assignment.course,
        "Subject": assignment.subject
        }
    assignment_form = forms.AssignmentForm(initial=initial)
    context = {
        "single_assignment": assignment,
        "assignment_id": id,
        "assignment": assignment_form
    }
    return render(request, 'student_exam/assignment_detail.html', context=context)




@login_required
def delete_assignment(request, id):
    
    assignment = Assignment.objects.get(id=id)
    user_id = assignment.user_id
    print('The assigmment: ',assignment)
    if user_id == request.user.id:
      
        assignment.delete()
        messages.success(request, "Assignment was successfully deleted")
        return redirect('dashboard')
    else:
        context = {
            "single_assignment": assignment,
            "assignment_id": id
        }
        messages.error(request, "You are not authorized to carry out this operation")
        return render(request, 'student_exam/assignment_detail.html', context=context)




@login_required
def submit_assignment(request, id):

    
    if is_ajax(request=request):
        template_name =  "student_exam/edit_submission_inner.html"
    else:
        template_name =  "student_exam/submission.html"

    assignment = Assignment.objects.get(id=id)
    submission_form = forms.SubmissionForm(request.POST, request.FILES)
    # if 'passcode' not in request.session.keys() or request.session['passcode'] != assignment.passcode:
    #     return redirect('pre_submission', id=id)
    # else:
    if assignment.due_date > datetime.date.today():
        if request.method == "POST":
            if submission_form.is_valid():
                user = request.user
                submission = submission_form.save(commit=False)
                submission.user_id = request.user.id
                submission.assignment_id = id
                user.matric_number = uuid4()
                submission.matric_number = user.matric_number
                submission.save()
                messages.success(request, 'Assignment was successfully submitted.')
                return redirect('submission-detail', id=submission.id)
            else:
                for error in submission_form.errors.values():
                        messages.error(request, error)
        context = {
            "submission": submission_form,
            "assignment_id": id,
            "assignment": assignment
        }
        return render(request, template_name, context=context)
    else:
        context = {
            "assignment_id": id,
        }
        messages.info(request, 'Sorry,the due date for this assignment is passed!')
        return redirect('dashboard')




@login_required
def submission_detail(request, id):
    submission = Submission.objects.get(id=id)
    context = {
        "single_submission": submission,
        "submission_id": id
    }
    return render(request, 'student_exam/submission_detail.html', context=context)

@login_required
def delete_submission(request, id):
    submission = Submission.objects.get(id=id)
    if submission.user_id == request.user.id:
        submission.delete()
        return redirect('dashboard')
    else:
        context = {
            "single_submission": submission,
            "submission_id": id
        }
        messages.error(request, "You are not authorized to carry out this operation")
        return render(request, 'student_exam/submission-detail.html', context=context)


@login_required
def edit_submission(request, id):

   
    submission = Submission.objects.get(id=id)
    assignment_id = submission.assignment_id
    assignment = Assignment.objects.get(id=assignment_id)
    user_id = submission.user_id
    initial = {
        "answer": submission.answer,
        "upload": submission.upload
        }
       
    if is_ajax(request=request) and request.method=='GET':
        template_name =  "student_exam/edit_submission_inner.html"
        submission_form = forms.SubmissionForm(instance=submission)
        context={'submission':submission_form,'submission_id':id}
        return render(request, template_name, context=context)
    else:
        template_name =  "student_exam/submission_detail.html"

    submission_form = forms.SubmissionForm(request.POST, request.FILES, instance=submission, initial=initial)
    if request.method == "POST":
        if assignment.due_date > datetime.date.today():
            if submission_form.is_valid():
                current_user = request.user.id
                if current_user == user_id:
                    submission_form.save()
                    submission.last_updated = datetime.date.today()
                    submission.save()
                    messages.success(request, 'Submission was successfully edited.')
                    new_data = Submission.objects.last()
                    return redirect('submission-detail', id=new_data.id)
                else:
                    messages.error(request, "You are not authorized to carry out this operation")
            else:
                for error in submission_form.values():
                    messages.error(request, error)
                
        else:
            messages.error(request, "The due date for this assignment has passed")
    context = {
        "submission": submission_form,
        "submission_id": id,
        "single_submission": submission
    }
    return render(request, template_name, context=context)




@login_required
def edit_assignment(request, id):
    
    
    assignment = Assignment.objects.get(id=id)
    user_id = assignment.user_id

    initial = {
        "title": assignment.title,
        "content": assignment.content,
        "attachement": assignment.upload,
        "due_date": assignment.due_date,
        "class": assignment.course,
        "subject": assignment.subject
        }
    assignment_form = forms.AssignmentForm(instance=assignment)

    if is_ajax(request=request) and request.method == 'GET':
        assignment_form = forms.AssignmentForm(instance=assignment)
        template_name =  "student_exam/edit_assignment_inner.html"
        # assignment_form = forms.AssignmentForm()
        context= {'assignment':assignment_form,'assignment_id': id}
        return render(request, template_name, context=context)

    if request.method == "POST":
        assignment_form = forms.AssignmentForm(request.POST, request.FILES, instance=assignment, initial=initial)
        if assignment_form.is_valid():
            current_user = request.user.id
            if current_user == user_id:
                assignment_form.save()
                assignment.last_updated = datetime.date.today()
                assignment.save()
                messages.success(request, 'Assignment was successfully edited.')
                new_data = Assignment.objects.last()
                return redirect('assignment-detail', id=new_data.id)
            else:
                messages.error(request, "You are not authorized to carry out this operation")
        else:
            for error in assignment_form.errors.values():
                messages.error(request, error)
            
    context = {
        "assignment": assignment_form,
        "assignment_id": id
    }
    return render(request, "student_exam/assignment_detail.html", context=context)


def pre_submission(request, id):
    if not request.user.is_authenticated():
      return redirect('/')  
    pass_form = forms.PassForm(request.POST or None)
    if request.method == "POST":
        assignment = Assignment.objects.get(id=id)
        if pass_form.is_valid():
            passcode = request.POST["passcode"]
            if passcode == assignment.passcode:
                request.session['passcode'] = passcode
                return redirect('assignment_submission', id=id)
            else:
                messages.error(request, "Passcode does not match")
        else:
            for error in pass_form.errors.values():
                messages.error(request, error)

    submission_form = forms.SubmissionForm()
    context = {
        "pass": pass_form,
        "assignment_id": id,
        "submission": submission_form
    }
    return render(request, "/pass.html", context)


'''|Extra views for the gradebook'''
def context_data(request):
    fullpath = request.get_full_path()
    abs_uri = request.build_absolute_uri()
    abs_uri = abs_uri.split(fullpath)[0]
    context = {
        'system_host' : abs_uri,
        'page_name' : '',
        'page_title' : '',
        'system_name' : 'jSchoolWeb',
    }

    return context

@login_required
def gradebook(request):
    context = context_data(request)
    context['page'] = 'book'
    context['page_title'] = "Book List"
    context['books'] = Gradebook.objects.all().order_by('-lb')
    return render(request, 'student_exam/gradebook.html', context)

@login_required
def save_gradebook(request):
    resp = { 'status': 'failed', 'msg' : '' }
    print(request)
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            gradebook = Gradebook.objects.get(id = post['id'])
            form = forms.SaveGradebook(request.POST, instance=gradebook)
        else:
            form = forms.SaveGradebook(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Gradebook saved successfully.")
            else:
                messages.success(request, "Book updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "No data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def view_gradebook(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_gradebook'
    context['page_title'] = 'View GradeBook'
    if pk is None:
        context['books'] = {}
    else:
        context['books'] = Gradebook.objects.get(id=pk)
    
    return render(request, 'student_exam/view_gradebook.html', context)

@login_required
def manage_gradebook(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_gradebook'
    context['page_title'] = 'Manage GradeBook'
   
    if pk is None:
        context['book'] = {}
    else:
        context['book'] = Gradebook.objects.get(id=pk)
    print('context:',context)
    return render(request, 'student_exam/manage_gradebook.html', context)

@login_required
def delete_gradebook(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'ID is invalid'
    else:
        try:
            Gradebook.objects.filter(pk = pk).delete()
            messages.success(request, "gradebook line deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")




'''|Extra views for the OverallGradebook'''

@login_required
def overall_gradebook(request):
    context = context_data(request)
    context['page'] = 'book'
    context['page_title'] = "Book List"
    context['books'] = OverallGradebook.objects.all().order_by('-lb')
    return render(request, 'student_exam/overall_gradebook.html', context)

@login_required
def save_overall_gradebook(request):
    resp = { 'status': 'failed', 'msg' : '' }
    print(request)
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            gradebook = OverallGradebook.objects.get(id = post['id'])
            form = forms.SaveOverallGradebook(request.POST, instance=gradebook)
        else:
            form = forms.SaveOverallGradebook(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Gradebook saved successfully.")
            else:
                messages.success(request, "Book updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "No data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def view_overall_gradebook(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_gradebook'
    context['page_title'] = 'View GradeBook'
    if pk is None:
        context['books'] = {}
    else:
        context['books'] = OverallGradebook.objects.get(id=pk)
    
    return render(request, 'student_exam/view_overall_gradebook.html', context)

@login_required
def manage_overall_gradebook(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_gradebook'
    context['page_title'] = 'Manage GradeBook'
   
    if pk is None:
        context['book'] = {}
    else:
        context['book'] = OverallGradebook.objects.get(id=pk)
    print('context:',context)
    return render(request, 'student_exam/manage_overall_gradebook.html', context)

@login_required
def delete_overall_gradebook(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'ID is invalid'
    else:
        try:
            OverallGradebook.objects.filter(pk = pk).delete()
            messages.success(request, "gradebook line deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")