from student_exam.models import Gradebook

def score_grade2(score):
    if score >= 70:
        return "A"
    elif score >=60:
        return "B"
    elif score >= 50:
        return "C"
    elif score >=40:
        return "D"
    elif score>=30:
        return "E"
    else:
        return "F"


def score_grade(score):

    gradescale = Gradebook.objects.values_list('lb','grade','remark').order_by('-lb')
    for (lb, grade,remark) in gradescale:

        if score >= lb:
            return (grade,remark,)
            break
        else:
            continue
       