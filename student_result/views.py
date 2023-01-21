from sys import exec_prefix
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render,  get_object_or_404
from django.views.generic import DetailView, ListView, View

from django.db.models import Q

from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse, Http404
from io import BytesIO

from student_core.models import Courses, Students as Student
from student_result.utils import score_overall_grade,renderPdf

from .forms import CreateResults, EditResults
from .models import Result
from student_exam.models import Gradebook


@login_required
def create_result(request,clsid):
    students = Student.objects.all().filter(course_id=clsid)
    if request.method == "POST":
       
        # after visiting the second page
        if "finish" in request.POST:
           
            form = CreateResults(request.POST)
            if form.is_valid():
               
                subjects = form.cleaned_data["subjects"]
                session = form.cleaned_data["session"]
                term = form.cleaned_data["term"]
                students = request.POST["students"]
                print('Posted here',students)
                results = []
                for student in students.split(","):
                    stu = Student.objects.get(pk=student)
                    if stu.course_id:
                        for subject in subjects:
                            check = Result.objects.filter(
                                session=session,
                                term=term,
                                current_class=stu.course_id,
                                subject=subject,
                                student=stu,
                            ).first()
                            if not check:
                                results.append(
                                    Result(
                                        session=session,
                                        term=term,
                                        current_class=stu.course_id,
                                        subject=subject,
                                        student=stu,
                                    )
                                )
                            else:
                                 messages.warning(request, "Mark Sheet for this student already exists, You could only edit")

                Result.objects.bulk_create(results)
                
                return redirect("edit-results",clsid=clsid,students=students)

        # after choosing students
        id_list = request.POST.getlist("students")
       
        if id_list:
            form = CreateResults(
                initial={
                    "session": request.current_session,
                    "term": request.current_term,
                }
            )
            studentlist = ",".join(id_list)
            context = {"students": studentlist, "form": form, "count": len(id_list)}
            return render(
                request,
                "student_result/create_result_page2.html",context,
            )
        else:
            messages.warning(request, "You didnt select any student.")
    return render(request, "student_result/create_result.html", {"students": students})


@login_required
def edit_results(request,clsid,students):
    
    ids = [eval(i) for i in [students]]
    #not_ids = Student.objects.exclude(id__in=[ids])
    print('set ', ids)
    if request.method == "POST":
        form = EditResults(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Results successfully updated")
           
            return redirect("edit-results",clsid=clsid,students=students)
    else:
        results = Result.objects.filter(
            session=request.current_session, term=request.current_term,current_class=clsid
            ).exclude(~Q(student__in=ids))
    
        form = EditResults(queryset=results)
    return render(request, "student_result/edit_results.html", {"formset": form})


from school.models import School
class ResultListView(LoginRequiredMixin, View):


    def get(self, request, *args, **kwargs):
        results = Result.objects.filter(
            session=request.current_session, term=request.current_term
        )
        bulk = {}
        
        for result in results:
            test_total = 0
            exam_total = 0
            subjects = []
            for subject in results:
                if subject.student == result.student:
                    subjects.append(subject)
                    test_total += subject.test_score
                    exam_total += subject.exam_score

            bulk[result.student.id] = {
                "student": result.student,
                "subjects": subjects,
                "test_total": test_total,
                "exam_total": exam_total,
                "total_total": test_total + exam_total,
            }

        context = {"results": bulk}
       
        return render(request, "student_result/all_results.html", context)


@login_required
def ResultDetailView(request,student):
    # def get_context_data(self, request,**kwargs):
    #     context= super().get_context_data(**kwargs)
        try:
            school = School.objects.all().first()
        except:
            school={}

        try:
            gradeBook = Gradebook.objects.all().order_by('-lb')
        except:
            gradeBook={}

        results = Result.objects.filter(
            session=request.current_session, term=request.current_term,student=student
        )
        '''Extra Context Variables'''
        report_dates ={"closing":'',"opening":''}
        
        bulk = {}
        gradebook_with_ub=[]
        studentClass=''
        classSize=0
        overall_grade=[]
        for result in results:
            test_total = 0
            exam_total = 0
            subjects = []
            for subject in results:
                if subject.student == result.student:
                    subjects.append(subject)
                    test_total += subject.test_score
                    exam_total += subject.exam_score

            total_total=test_total + exam_total
            '''Extra data for report header'''
            studentClass= result.student.course_id
            classSize = Student.objects.filter(course_id=studentClass).count()
            overall_grade = score_overall_grade(total_total)
            #studentClass = Courses.objects.get(id=studentClass).values('name')
            report_dates['closing']= str(request.current_session).split('to',1)[1]
            report_dates['opening']=request.current_session.re_opening_date
           
            grade_lb_list = list(gradeBook)
            grade_ub_list =[100]

            for i in range(len(grade_lb_list[:-1])):
                grade_ub_list.append(grade_lb_list[i].lb-1)
            
            gradebook_with_ub =zip(gradeBook,grade_ub_list)

            bulk[result.student.id] = {
                "student": result.student,
                "subjects": subjects,
                "test_total": test_total,
                "exam_total": exam_total,
                "total_total":total_total,
                "school":school,
                'gradeBook':gradebook_with_ub,
                "Class":studentClass,
                "ClassSize":classSize,
                "overall_grade":overall_grade,
                "report_dates":report_dates               
                 }
           
      
        context = {"results": bulk}
        
        return render(request, "student_result/all_results.html", context)


'''Class Results Details'''


@login_required
def ClassResultDetailView(request,clsid):
    # def get_context_data(self, request,**kwargs):
    #     context= super().get_context_data(**kwargs)
        try:
            school = School.objects.all().first()
        except:
            school={}

        try:
            gradeBook = Gradebook.objects.all().order_by('-lb')
        except:
            gradeBook={}
        #studentClass = Courses.objects.get(id=studentClass).values('name')
        student_list =Student.objects.filter(course_id=clsid) 
        bulk = {}
        for student in student_list:
            results = Result.objects.filter(session=request.current_session, term=request.current_term,student=student.id)

        #class_name = Courses.objects.get(id=clsid)
        
            print("Results:",results)

            '''Extra Context Variables'''
            report_dates ={"closing":'',"opening":''}
         
            gradebook_with_ub=[]
            studentClass=''
            classSize=0
            overall_grade=[]
            for result in results:
                test_total = 0
                exam_total = 0
                subjects = []
                for subject in results:
                    if subject.student == result.student:
                        subjects.append(subject)
                        test_total += subject.test_score
                        exam_total += subject.exam_score

                total_total=test_total + exam_total

                '''Extra data for report header'''
                studentClass= result.student.course_id
                classSize = Student.objects.filter(course_id=studentClass).count()
                overall_grade = score_overall_grade(total_total)
             
                report_dates['closing']= str(request.current_session).split('to',1)[1]
                report_dates['opening']=request.current_session.re_opening_date
                
                grade_lb_list = list(gradeBook)
                grade_ub_list =[100]

                for i in range(len(grade_lb_list[:-1])):
                    grade_ub_list.append(grade_lb_list[i].lb-1)
                
                gradebook_with_ub =zip(gradeBook,grade_ub_list)

                bulk[result.student.id] = {
                    "student": result.student,
                    "subjects": subjects,
                    "test_total": test_total,
                    "exam_total": exam_total,
                    "total_total":total_total ,
                    "overall_grade":overall_grade,"school":school,
                    'gradeBook':gradebook_with_ub,
                    "Class":studentClass,
                    "ClassSize":classSize,
                    "report_dates":report_dates
                }
               
                # for i,j in gradebookall:
                #     print("Zip list:", i,j,i.lb,i.remark)
            results={}
        print("Bulk results: ",bulk)
        context = {"results": bulk}
        
        return render(request, "student_result/all_results_list.html", context)


@login_required
def find_result(request):
    
    classes = Courses.objects.all()
    if request.method == "POST":
        data = request.POST
        pk=0

        print('data: ',data)
        # data = json.loads(form)
        try:
            id = data['studentid']
            id2 = data['student']
        except:
            pass
        try:
            pk= id if (id and id.strip()) else id2
            #print('pk :', id)
        except:
            redirect('find-result')

        if(pk=='All'):
            return redirect('get-class-result',clsid=data['classes'])
        else:
            return redirect('get-result',student=pk)

    return render(request, 'student_result/find_result.html', {'class':classes})

@login_required
def select_result_class(request):
    classes = Courses.objects.all()
    students=None
    if request.method == "POST":
        data = request.POST
        #clsid=0
        try:
        
            clsid = data['classes']
            #classes = Courses.objects.all().filter(id=clsid)
        #students = Student.objects.filter(course_id=clsid)
        except:
            # classes = Courses.objects.all()
            #return redirect('select-result-class')
            cls_id=0
        return redirect('create-result', clsid=clsid)

    return render(request, 'student_result/select_class.html', {'class':classes})

def load_students(request):
    cls_id = request.GET.get('cls_id')
    students = Student.objects.filter(course_id=cls_id)
    return render(request, 'student_result/student_dropdown.html', {'students': students})



class pdf(View):
    def get(self,request):
        context= {}
        article_pdf = renderPdf("student_result/all_results.html", context)
        return HttpResponse(article_pdf, content_type='application/pdf')
