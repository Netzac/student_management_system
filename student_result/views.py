from ast import Not
from distutils import dist
from inspect import signature
from sys import exec_prefix
import math
from tokenize import Number, String
from unittest import result
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render,  get_object_or_404
from django.views.generic import DetailView, ListView, View

from django.db.models import F,Q,Count,Avg,Case,When,Value,Sum,Min,Max

from numpy import empty


from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse, Http404
from io import BytesIO

from student_core.models import Attendance, ClassTeacher, ConductInterestRemarks, Courses, Students as Student, Subjects
from student_result.utils import get_teacher_cls_id, score_overall_grade,renderPdf
from student_core.forms import ConductInterestRemarksFormset
from .forms import CreateResults, EditResults,EditExResults
from .models import ClassExercise, Result,ResultSummary
from student_exam.models import Gradebook,Exercise,OverallGradebook


@login_required
def create_result(request,clsid):
    students = Student.objects.all().filter(course_id=clsid)
    sheet_exists= False
    if request.method == "POST":
       
        # after visiting the second page
        if "finish" in request.POST:
           
            form = CreateResults(request.POST)
            if form.is_valid():
               
                subjects = form.cleaned_data["subjects"]
                session = form.cleaned_data["session"]
                term = form.cleaned_data["term"]
                students = request.POST["students"]
                print('Students again:',students)
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
                                sheet_exists=True
                if sheet_exists:  
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
            print("Students:" ,studentlist)
            context = {"students": studentlist, "form": form, "count": len(id_list)}
            return render(
                request,
                "student_result/create_result_page2.html",context,
            )
         
            messages.warning(request, "You didnt select any student.")
    return render(request, "student_result/create_result.html", {"students": students})


@login_required
def edit_results(request,clsid,students):
    
    ids =[int(i) for i in students.split(',')]
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
            ).exclude(~Q(student__in=ids)).annotate(studnet_count=Count('student')).order_by('subject')
        # results = Result.objects.filter(
        # session=request.current_session, term=request.current_term,current_class=clsid
        # ).in_bulk(ids)
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
        session =request.current_session
        term = request.current_term

        try:
            school = School.objects.all().first()
        except:
            school={}

        try:
            gradeBook = Gradebook.objects.all().order_by('-lb')
        except:
            gradeBook={}

        results = Result.objects.filter(
            session=session, term=term,student=student
        )
        '''Extra Context Variables'''
        report_dates ={"closing":'',"opening":''}
        
        bulk = {}
        gradebook_with_ub=[]
        studentClass=''
        classSize=0
        overall_grade=[]
        computeChart =True
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
            term_attendance_res = Attendance.objects.filter(student_id=student,session_year_id=request.current_session_id)
            total_attendance= term_attendance_res.count()
            student_attendance= term_attendance_res.aggregate(stu_attendance=Count(Case(When(status=True,then=1))))['stu_attendance']
            conductInterestRemarks =get_object_or_404(ConductInterestRemarks,student=student)
            studentClass= result.student.course_id
            classSize = Student.objects.filter(course_id=studentClass).count()
            overall_grade = score_overall_grade(total_total)
            #studentClass = Courses.objects.get(id=studentClass).values('name')
            report_dates['closing']= str(request.current_session).split('to',1)[1]
            report_dates['opening']=request.current_session.re_opening_date
            teacher = ClassTeacher.objects.get(cls_id=studentClass)
            print("Teacher:", teacher.staff_id.signature,)
            grade_lb_list = list(gradeBook)
            grade_ub_list =[100]

            for i in range(len(grade_lb_list[:-1])):
                grade_ub_list.append(grade_lb_list[i].lb-1)
            
            gradebook_with_ub =zip(gradeBook,grade_ub_list)
            if computeChart:
                 graph_data = get_chart_data(result.student,session,term)
                 computeChart=True
                 
            bulk[result.student.id] = {
                "student": result.student,
                "pic": result.student.profile_pic,
                "subjects": subjects,
                "test_total": test_total,
                "exam_total": exam_total,
                "total_total":total_total,
                "school":school,
                'gradeBook':gradebook_with_ub,
                "Class":studentClass,
                "staff": teacher.staff_id,
                "ClassSize":classSize,
                "overall_grade":overall_grade,
                "report_dates":report_dates,
                "total_attendance":total_attendance,
                "student_attendance":student_attendance,
                "cir":conductInterestRemarks,
                "graph":graph_data          
                 }
            get_result_summary(student,session,term,total=total_total,grade=overall_grade,attendance=total_attendance)
      
        mean_labels,subject_labels= get_chart_labels()
        graph_labels ={"mean_labels":mean_labels,
                    "subject_labels":subject_labels
        }
        #print("Bulk results: ",bulk[2]['graph'])
        context = {"results": bulk,"graph":graph_labels}
       
        return render(request, "student_result/all_results.html", context)


'''Class Results Details'''


@login_required
def ClassResultDetailView(request,clsid):
    # def get_context_data(self, request,**kwargs):
    #     context= super().get_context_data(**kwargs)
        session =request.current_session
        term = request.current_term
        computeChart=True
       
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
            results = Result.objects.filter(session=session, term=term,student=student.id)

        #class_name = Courses.objects.get(id=clsid)
        
            #print("Results:",results)

            '''Extra Context Variables'''
            report_dates ={"closing":'',"opening":''}
            total_total=0
            total_attendance=0
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
                term_attendance_res = Attendance.objects.filter(student_id=student,session_year_id=request.current_session_id)
                total_attendance= term_attendance_res.count()
                student_attendance= term_attendance_res.aggregate(stu_attendance=Count(Case(When(status=True,then=1))))['stu_attendance']
                conductInterestRemarks =get_object_or_404(ConductInterestRemarks,student=student)
                #print("Student_attendance:", student_attendance['stu_attendance'])
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

                if computeChart:
                 graph_data = get_chart_data(result.student,session,term)
                 computeChart=True

                bulk[result.student.id] = {
                    "student": result.student,
                    "pic": result.student.profile_pic,
                    "subjects": subjects,
                    "test_total": test_total,
                    "exam_total": exam_total,
                    "total_total":total_total ,
                    "overall_grade":overall_grade,
                    "school":school,
                    'gradeBook':gradebook_with_ub,
                    "Class":studentClass,
                    "ClassSize":classSize,
                    "report_dates":report_dates,
                    "total_attendance":total_attendance,
                    "student_attendance":student_attendance,
                    "cir":conductInterestRemarks,
                    "graph":graph_data,
                   
                }
               
                # for i,j in gradebookall:
                #     print("Zip list:", i,j,i.lb,i.remark)
            get_result_summary(student,session,term,total=total_total,grade=overall_grade,attendance=total_attendance)
           
            results={}
        mean_labels,subject_labels= get_chart_labels()
        graph_labels ={"mean_labels":mean_labels,
                    "subject_labels":subject_labels
        }
        #print("Bulk results: ",bulk[2]['graph'])
        context = {"results": bulk,"graph":graph_labels}
        
        return render(request, "student_result/all_results_list.html", context)


@login_required
def find_result(request):
    classes = Courses.objects.all()

    user_type = request.user.user_type
    classes = Courses.objects.all()

    if user_type=='2':
        classes= classes.filter(id=get_teacher_cls_id(request))
    

        
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
    user_type = request.user.user_type
    classes = Courses.objects.all()

    if user_type=='2':

        classes= classes.filter(id=get_teacher_cls_id(request))
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

@login_required
def select_ex_class(request):
    user_type = request.user.user_type
    template_name = 'student_result/select_class.html'

    classes = Courses.objects.all()
    ''' Teacher zone'''
    if user_type=='2':
        template_name = 'student_result/staff_select_class.html'

        cls_id = get_teacher_cls_id(request)
        classes = classes.filter(id=cls_id)
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
        return redirect('create-ex-result', clsid=clsid)

    return render(request,template_name, {'class':classes})



@login_required
def create_ex_result(request,clsid):
    students = Student.objects.all().filter(course_id=clsid)
    sheet_exists= False
    if request.method == "POST":
       
        # after visiting the second page
        if "finish" in request.POST:
           
            form = CreateResults(request.POST)
            if form.is_valid():
               
                subjects = form.cleaned_data["subjects"]
                session = form.cleaned_data["session"]
                term = form.cleaned_data["term"]
                students = request.POST["students"]
                exercises = Exercise.objects.all()
                
                results = []
                msg_added=False
                for student in students.split(","):
                    stu = Student.objects.get(pk=student)
                    if stu.course_id:
                        
                        for subject in subjects:
                           
                            for ex in exercises:
                                #print('Students again in Exercise:',students)
                                check = ClassExercise.objects.filter(
                                    session=session,
                                    term=term,
                                    current_class=stu.course_id,
                                    subject=subject,
                                    exercise=ex,
                                    student=stu,

                                ).first()
                                if not check:
                                    results.append(
                                        ClassExercise(
                                        session=session,
                                        term=term,
                                        current_class=stu.course_id,
                                        subject=subject,
                                        exercise=ex,
                                        student=stu,
                                        )
                                    )
                                else:
                                    sheet_exists=True
                if sheet_exists and not msg_added:  
                    messages.warning(request, "Mark Sheet for this student already exists, You could only edit")
                    msg_added=True

                ClassExercise.objects.bulk_create(results)
                load_class_scores(session,term,clsid,students)
                return redirect("edit-ex-results",clsid=clsid,students=students)

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
            print("Students from ex:" ,studentlist)
            context = {"students": studentlist, "form": form, "count": len(id_list)}
            return render(
                request,
                "student_result/create_result_page2.html",context,
            )
         
            messages.warning(request, "You didnt select any student.")
    return render(request, "student_result/create_result.html", {"students": students})


@login_required
def edit_ex_results(request,clsid,students):
    print("students",students)
    ids =[int(i) for i in students.split(',')]
    #not_ids = Student.objects.exclude(id__in=[ids])
    print(' |Ex set ', ids)
    if request.method == "POST":
        form = EditExResults(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Results successfully updated")
           
            return redirect("edit-ex-results",clsid=clsid,students=students)
    else:
        results = ClassExercise.objects.filter(
            session=request.current_session, term=request.current_term,current_class=clsid
            ).exclude(~Q(student__in=ids)).annotate(student_count=Count('student')).order_by('subject')
        # results = Result.objects.filter(
        # session=request.current_session, term=request.current_term,current_class=clsid
        # ).in_bulk(ids)
        form = EditExResults(queryset=results)
    return render(request, "student_result/edit_ex_results.html", {"formset": form})



def load_class_scores(current_session,current_term,clsid,students):
    ids =[int(i) for i in students.split(',')]
   
    total_num_ex = Exercise.objects.count()
    results = Result.objects.filter(
        session=current_session, term=current_term,current_class=clsid
        ).exclude(~Q(student__in=ids))
   
    # results = Result.objects.filter(
    # session=request.current_session, term=request.current_term,current_class=clsid
    # ).in_bulk(ids)
    all_scores ={}
    for result in results:
        check = ClassExercise.objects.filter(
                                    session=result.session,
                                    term=result.term,
                                    current_class=result.current_class,
                                    subject=result.subject,
                                    student=result.student,
                                ).first()
    
        if check:
           res= ClassExercise.objects.filter(
            session=result.session,
            term=result.term,
            current_class=result.current_class,
            subject=result.subject,
            student=result.student,
            ).aggregate(Sum('score'))

           '''Update Exams Results'''
           Result.objects.filter(
           session=result.session,
           term=result.term,
           current_class=result.current_class,
           subject=result.subject,
           student=result.student,
            ).update(test_score=math.ceil(res['score__sum']))
           
           #print('Ex score is',math.ceil(res['score__avg']))
    return None

from django.db import transaction
def get_result_summary(student,session,term,**kwargs):

    data = kwargs
    #print("Student type",type(student))
    if  type(student) is str:
        stud = Student.objects.get(id=student)
    else:
        stud=student

    ResultSummary.objects.filter(student=stud,session=session,term=term).delete()
    instance, created = ResultSummary.objects.get_or_create(student=stud,session=session,term=term,**data)

    if not created:
        with transaction.atomic():
            #for k,v in data.items():
            ResultSummary.objects.filter(student=student).update(total=data['total'],grade=data['grade'],attendance=data['attendance'])

    return None

def get_chart_data(student,session,term):
    ''' Returns a tuple of computed values as data and graph labels'''
    means =[]
    data ={}
    subj_total=[]
    cls_subj_avg =[]
    test_scores=[]
    cls_test_avg=[]
    #data['labels']=labels
    
    cls = student.course_id #Courses.objects.filter(id=student.course_id)
    cls_list =cls.students_set.all()
    print('class list is', cls_list)
    ''' Computing student means'''
    rs= ResultSummary.objects.filter(student__in=cls_list)
    student_score =rs.filter(student=student.id).aggregate( Sum("total"))['total__sum']
    cls_avg =rs.aggregate(Avg("total"))['total__avg']
    cls_min = rs.aggregate(Min("total"))['total__min']
    cls_max =rs.aggregate(Max("total"))['total__max']
    means.extend([student_score,cls_min,cls_avg,cls_max])
    data['means']= means

    '''Computing total score per subject '''
    all_result = Result.objects.select_related("subject").all()
    result = all_result.filter(student=student)

    subjects= result.annotate(subject_total=(F("test_score")+F("exam_score")))
    class_subjects = all_result.values('subject').annotate(cls_avg=(Avg((F("test_score")+F("exam_score")))))

    tests= result.values('test_score')
    class_tests = all_result.values('subject').annotate(test_avg=(Avg((F("test_score")))))

    for sub in subjects:
        subj_total.append(sub.subject_total)
    data["subjects"] = subj_total
    data['subjects_avg'] =cls_subj_avg

    for sub in class_subjects:
       cls_subj_avg.append(sub['cls_avg'])
       #print("class_avg is", sub['cls_avg'])

    for test in tests:
       #cls_subj_avg.append(sub['cls_avg'])
       test_scores.append( test['test_score'])
       
    for test in class_tests:
       #cls_subj_avg.append(sub['cls_avg'])
       cls_test_avg.append( test['test_avg'])
       print("test avgs:",test['test_avg'])

    data['tests'] =test_scores
    data['tests_avg'] =cls_test_avg    
    return data

def get_chart_labels():
    mean_labels =['Student Overall Score','Class Min','Class Average','Class Max']
    subjects_labels = get_subject_list()

    return mean_labels,subjects_labels



'''cir abbreviation for conduct interest remarks'''
@login_required
def select_cir_class(request):
    classes = Courses.objects.all()
    students=None

    user_type = request.user.user_type
    classes = Courses.objects.all()

    if user_type=='2':

        classes= classes.filter(id=get_teacher_cls_id(request))
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
        return redirect('create-conduct-interest-remarks', clsid=clsid)

    return render(request, 'student_result/select_class.html', {'class':classes})

@login_required
def create_conduct_interest_remarks(request,clsid):
    students = Student.objects.all().filter(course_id=clsid)
    sheet_exists= False

    if request.method == "POST":
        id_list = request.POST.getlist("students")
        student_list = ",".join(id_list)
        if not id_list:
            messages.warning(request, "You did not select any student.")
            return redirect('create-conduct-interest-remarks', clsid=clsid)
        print("I am valid:",id_list)
        results = []
        for student in id_list:
            stu = Student.objects.get(pk=student)
            if stu:
                check = ConductInterestRemarks.objects.filter(
                    student=stu,
                ).first()
                if not check:
                    results.append(
                        ConductInterestRemarks(
                        student=stu,
                        )
                    )
                else:
                    sheet_exists=True
        if sheet_exists:  
            messages.warning(request, "Sheet for this student(s) already exists, You could only edit")
            

        ConductInterestRemarks.objects.bulk_create(results)
        print('Students before passing ',student_list)
        return redirect("edit-conduct-interest-remarks",clsid=clsid,students=student_list)

        # after choosing students
    return render(request, "student_result/create_result.html", {"students": students})


@login_required
def edit_conduct_interest_remarks(request,clsid,students):
    print("students: ",students)
    ids =[int(i) for i in students.split(',')]
    #ids = " ".join(students)
    #not_ids = Student.objects.exclude(id__in=[ids])
    print(' New set ', ids)
    if request.method == "POST":
        form = ConductInterestRemarksFormset(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sheet successfully updated")
           
            return redirect("edit-conduct-interest-remarks",clsid=clsid,students=students)
    else:
        results = ConductInterestRemarks.objects.exclude(~Q(student__in=ids)).order_by('student')
        # results = Result.objects.filter(
        # session=request.current_session, term=request.current_term,current_class=clsid
        # ).in_bulk(ids)
        form = ConductInterestRemarksFormset(queryset=results)
    return render(request, "student_result/edit_conduct_interest_remarks.html", {"formset": form})

#from django.db.models import F
def promote_students(request):
    
    
    context ={}
    if request.method=='POST':
        data = request.POST
        grade=""
        crit = data['crit']
        if 'grade' in data:
             grade = data['grade']
        print('Data:',data,grade,crit)
        if crit =="":
             messages.error(request,"Criterion must be selected")
             return redirect('promote-students')
        elif crit=="2" and grade=="0":
             messages.error(request,"Grade must be selected")
             return redirect('promote-students')
        
        highest_class = Courses.objects.values('id').last()
        print("hight class",highest_class['id'])
        completed_students = Student.objects.filter(course_id__in = [highest_class['id']])
        '''Promotion criterion has been set as overall grade cutoff'''
        if crit =="2":
           
            students_to_demote = ResultSummary.objects.filter(Q(grade__gte=grade) | Q(student__course_id=highest_class['id'])).values('student')
        else:
             students_to_demote = ResultSummary.objects.filter(Q(student__course_id=highest_class['id'])).values('student')
        
        print("To demote:", students_to_demote,highest_class['id'],grade)
        with transaction.atomic():
             Student.objects.exclude(id__in =students_to_demote).update(course_id=F("course_id")+1)
             completed_students.update(status='3')

        res = Student.objects.exclude(id__in =students_to_demote)
        print("Promted ", res)
        messages.success(request,"Students successfully promoted ")
        return redirect('promote-students')
    return render(request,"student_result/promotion_criteria.html",context)


    
def load_students(request):
    cls_id = request.GET.get('cls_id')
    students = Student.objects.filter(course_id=cls_id)
    return render(request, 'student_result/student_dropdown.html', {'students': students})

def load_grades(request):
    crit_id = request.GET.get('crit_id')
    print("crit ", crit_id)
    if crit_id=="2":
        grades = OverallGradebook.objects.all().values('id','grade').order_by('grade')
    return render(request, 'student_result/grade_dropdown.html', {'grades': grades})



class pdf(View):
    def get(self,request):
        context= {}
        article_pdf = renderPdf("student_result/all_results.html", context)
        return HttpResponse(article_pdf, content_type='application/pdf')

def get_subject_list():
    subject_all = Subjects.objects.all()
    subject_list = []
    for subject in subject_all:
        subject_list.append(subject.subject_name)

    #print("Subject list", subject_list)
       
    return subject_list