from rest_framework import serializers
from student_core.models import (
    CustomUser, Students, Staffs, Courses, Subjects,
    SessionYearModel, AcademicTerm, Gender, Role, Bank,
    ClassTeacher, Attendance, LeaveReportStudent,
    LeaveReportStaff, StudentResult
)
from .serializers_helpers import get_lookup_field_value, safe_str

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'user_type']

class StudentsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='admin.username', write_only=True)
    first_name = serializers.CharField(source='admin.first_name')
    last_name = serializers.CharField(source='admin.last_name')
    email = serializers.EmailField(source='admin.email')
    course_name = serializers.CharField(source='course_id.course_name', read_only=True)
    session_name = serializers.CharField(source='session_year_id.name', read_only=True)
    gender_name = serializers.CharField(source='gender.gender_name', read_only=True)

    class Meta:
        model = Students
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'gender', 'gender_name', 'dob', 'address', 'profile_pic',
            'course_id', 'course_name', 'session_year_id', 'session_name',
            'status', 'parent_first_name', 'parent_last_name', 'parent_email',
            'parent_contact_number', 'parent_occupation'
        ]

    def create(self, validated_data):
        admin_data = validated_data.pop('admin')
        # Logic to create CustomUser first would go here
        # For this scaffold, we assume user creation happens via a higher service
        return super().create(validated_data)

class StaffsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='admin.username', write_only=True)
    first_name = serializers.CharField(source='admin.first_name')
    last_name = serializers.CharField(source='admin.last_name')
    email = serializers.EmailField(source='admin.email')
    role_name = serializers.CharField(source='role.type', read_only=True)
    gender_name = serializers.CharField(source='gender.gender_name', read_only=True)
    bank_name = serializers.CharField(source='bank.name', read_only=True)

    class Meta:
        model = Staffs
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'dob', 'gender', 'gender_name', 'role', 'role_name',
            'contact_number', 'address', 'status', 'bank', 'bank_name',
            'bank_acc_no'
        ]

class CoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = ['id', 'course_name']

class SubjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['id', 'subject_name']

class SessionYearModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionYearModel
        fields = ['id', 'name', 'session_start_year', 'session_end_year', 'current']

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = ['id', 'gender_name']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'type', 'description']

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['id', 'name']
