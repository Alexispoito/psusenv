from django.shortcuts import render
from django.views.generic.list import ListView

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from studentorg.models import Organization, OrgMember, Student, College, Program
from studentorg.forms import OrganizationForm, OrgMemberForm, StudentForm, CollegeForm, ProgramForm
from django.urls import reverse_lazy
from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from datetime import datetime, timedelta


@method_decorator(login_required, name='dispatch')
class HomePageView(ListView):
    model = Organization
    context_object_name = 'home'
    template_name = "home.html"

class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass
    
def orgMemDoughnutChart(request):
    with connection.cursor() as cursor:
        # Execute raw SQL query to count student members for each organization
        cursor.execute("""
            SELECT studentorg_organization.name, COUNT(studentorg_orgmember.id) AS student_count
            FROM studentorg_orgmember
            INNER JOIN studentorg_organization ON studentorg_orgmember.organization_id = studentorg_organization.id
            GROUP BY studentorg_organization.name
        """)
        # Fetch all rows from the cursor
        rows = cursor.fetchall()
        
    # Prepare data for the chart
    result = {name: count for name, count in rows}

    return JsonResponse(result)

def studentCountEveryCollege(request):
    # Query to count students for each college
    college_student_counts = Student.objects.values('program__college__college_name').annotate(student_count=Count('id'))

    # Prepare data for the chart
    result = {college['program__college__college_name']: college['student_count'] for college in college_student_counts}

    return JsonResponse(result)

def radarStudenCountEveryCollege(request):
    # Query to count students for each college
    college_student_counts = Student.objects.values('program__college__college_name').annotate(student_count=Count('id'))

    # Prepare data for the chart
    result = {college['program__college__college_name']: college['student_count'] for college in college_student_counts}

    return JsonResponse(result)

def programPolarchart(request):
    with connection.cursor() as cursor:
        # Execute raw SQL query to count student members for each program
        cursor.execute("""
            SELECT studentorg_program.prog_name, COUNT(studentorg_program.id) AS student_count
            FROM studentorg_program
            INNER JOIN studentorg_student ON studentorg_program.id = studentorg_student.program_id
            GROUP BY studentorg_program.prog_name
        """)
        # Fetch all rows from the cursor
        rows = cursor.fetchall()

        # Prepare data for the chart
        result = {name: count for name, count in rows}

    return JsonResponse(result)

from django.http import JsonResponse
from django.db import connection

def htmlLegendsChart(request):
    with connection.cursor() as cursor:
        # Execute raw SQL query to count student members for each organization and their month joined
        cursor.execute("""
            SELECT studentorg_organization.name, COUNT(studentorg_orgmember.id) AS student_count, STRFTIME('%m', studentorg_orgmember.date_joined) AS joined_month
            FROM studentorg_orgmember
            INNER JOIN studentorg_organization ON studentorg_orgmember.organization_id = studentorg_organization.id
            GROUP BY studentorg_organization.name, joined_month
        """)
        # Fetch all rows from the cursor
        rows = cursor.fetchall()
        
    # Prepare data for the chart
    result = {}
    for org_name, count, joined_month in rows:
        if org_name not in result:
            result[org_name] = {'student_count': {}, 'total_students': 0}
        result[org_name]['student_count'][joined_month] = count
        result[org_name]['total_students'] += count

    return JsonResponse(result)

class OrganizationList(ListView):
    model = Organization
    context_object_name ='organization'
    template_name = 'org_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(OrganizationList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get('q') != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) | 
                           Q(description__icontains=query))
        return qs


class OrganizationCreateView(CreateView):
    model = Organization
    form_class = OrganizationForm
    template_name= 'org_add.html'
    success_url = reverse_lazy('organization-list')

class OrganizationUpdateView(UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name= 'org_edit.html'
    success_url = reverse_lazy('organization-list')

class OrganizationDeleteView(DeleteView):
    model = Organization
    template_name= 'org_del.html'
    success_url = reverse_lazy('organization-list')

class OrgMemberList(ListView):
    model = OrgMember
    context_object_name = 'orgmember'
    template_name = 'orgmember_list.html'
    paginate_by = 5

class OrgMemberCreateView(CreateView):
    model = OrgMember
    form_class = OrgMemberForm
    template_name = 'orgmember_add.html'
    success_url = reverse_lazy('orgmember-list')
    
class OrgMemberUpdateView(UpdateView):
    model = OrgMember
    form_class = OrgMemberForm
    template_name = 'orgmember_edit.html'
    success_url = reverse_lazy('orgmember-list')

class OrgMemberDeleteView(DeleteView):
    model = OrgMember
    template_name = 'orgmember_del.html'
    success_url = reverse_lazy('orgmember-list')

class StudentList(ListView):
    model = Student
    context_object_name = 'student'
    template_name = 'student_list.html'
    paginate_by = 5

class StudentCreateView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'student_add.html'
    success_url = reverse_lazy('student-list')

class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'student_edit.html'
    success_url = reverse_lazy('student-list')

class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'student_del.html'
    success_url = reverse_lazy('student-list')

class CollegeList(ListView):
    model = College
    context_object_name = 'college'
    template_name = 'college_list.html'
    paginate_by = 5

class CollegeCreateView(CreateView):
    model = College
    form_class = CollegeForm
    template_name = 'college_add.html'
    success_url = reverse_lazy('college-list')
    

class CollegeUpdateView(UpdateView):
    model = College
    form_class = CollegeForm
    template_name = 'college_edit.html'
    success_url = reverse_lazy('college-list')

class CollegeDeleteView(DeleteView):
    model = College
    template_name = 'college_del.html'
    success_url = reverse_lazy('college-list')

class ProgramList(ListView):
    model = Program
    context_object_name = 'program'
    template_name = 'program_list.html'
    paginate_by = 5

class ProgramCreateView(CreateView):
    model = Program
    form_class = ProgramForm
    template_name = 'program_add.html'
    success_url = reverse_lazy('program-list')

class ProgramUpdateView(UpdateView):
    model = Program
    form_class = ProgramForm
    template_name = 'program_edit.html'
    success_url = reverse_lazy('program-list')

class ProgramDeleteView(DeleteView):
    model = Program
    template_name = 'program_del.html'
    success_url = reverse_lazy('program-list')