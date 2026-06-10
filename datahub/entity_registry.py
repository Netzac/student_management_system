from .registry import EntityRegistry, EntityConfig
from student_core.models import (
    CustomUser, Students, Staffs, Courses, Subjects,
    SessionYearModel, AcademicTerm, Gender, Role, Bank,
    ClassTeacher
)
from .serializers import (
    StudentsSerializer, StaffsSerializer, CoursesSerializer,
    SubjectsSerializer, SessionYearModelSerializer,
    GenderSerializer, RoleSerializer, BankSerializer
)

EntityRegistry.register(EntityConfig(
    slug="session-years",
    display_name="Academic Session",
    module="Configuration",
    import_sequence=1,
    model=SessionYearModel,
    serializer_class=SessionYearModelSerializer,
    description="The academic year or term groupings.",
    supports_import=True,
    supports_export=True,
    required_fields=["name", "session_start_year"]
))

EntityRegistry.register(EntityConfig(
    slug="genders",
    display_name="Genders",
    module="Configuration",
    import_sequence=2,
    model=Gender,
    serializer_class=GenderSerializer,
    supports_import=True,
    supports_export=True,
    required_fields=["gender_name"]
))

EntityRegistry.register(EntityConfig(
    slug="roles",
    display_name="Staff Roles",
    module="Configuration",
    import_sequence=3,
    model=Role,
    serializer_class=RoleSerializer,
    supports_import=True,
    supports_export=True,
    required_fields=["type"]
))

EntityRegistry.register(EntityConfig(
    slug="banks",
    display_name="Banks",
    module="Configuration",
    import_sequence=4,
    model=Bank,
    serializer_class=BankSerializer,
    supports_import=True,
    supports_export=True,
    required_fields=["name"]
))

EntityRegistry.register(EntityConfig(
    slug="classes",
    display_name="Classes / Courses",
    module="Academics",
    import_sequence=5,
    model=Courses,
    serializer_class=CoursesSerializer,
    description="Classes, Grades, or Courses offered.",
    supports_import=True,
    supports_export=True,
    required_fields=["course_name"]
))

EntityRegistry.register(EntityConfig(
    slug="subjects",
    display_name="Subjects",
    module="Academics",
    import_sequence=6,
    model=Subjects,
    serializer_class=SubjectsSerializer,
    supports_import=True,
    supports_export=True,
    required_fields=["subject_name"]
))

EntityRegistry.register(EntityConfig(
    slug="staff",
    display_name="Staff & Teachers",
    module="People",
    import_sequence=10,
    model=Staffs,
    serializer_class=StaffsSerializer,
    description="Teaching and administrative staff.",
    supports_import=True,
    supports_export=True,
    required_fields=["first_name", "last_name", "username", "email"]
))

EntityRegistry.register(EntityConfig(
    slug="students",
    display_name="Students",
    module="People",
    import_sequence=20,
    model=Students,
    serializer_class=StudentsSerializer,
    description="Student enrollment records.",
    supports_import=True,
    supports_export=True,
    required_fields=["first_name", "last_name", "username", "email", "course_id"]
))
