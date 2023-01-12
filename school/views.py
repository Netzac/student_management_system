from tkinter.tix import Form
from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .forms import SchoolForm
from .models import School

# Create your views here.

class SchoolCreateView(LoginRequiredMixin, CreateView):
    model = School
    form_class = SchoolForm

    field_list = [
        'School Name', 'Motto', 'Phone','Email', 'Address', 'Branch','Administrator','Admin Signature',
        'Logo','School Seal'
    ]

    def get_context_data(self, **kwargs):
        context = super(SchoolCreateView, self).get_context_data(**kwargs)
        context['main_page_title'] = 'School Creation'
        context['panel_name'] = 'School'
        context['panel_title'] = 'Create School'
        return context

class SchoolListView(LoginRequiredMixin, ListView):
    model = School
    field_list = [
        'School Name', 'Motto', 'Phone','Email', 'Address', 'Branch','Administrator','Admin Signature',
        'Logo','School Seal'
    ]
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_list']   =   self.field_list
        return context

class SchoolDetailView(LoginRequiredMixin, DetailView):
    model = School
    field_list = [
        'School Name', 'Motto', 'Phone','Email', 'Address', 'Branch','Administrator','Admin Signature',
        'Logo','School Seal'
    ]
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_list']   =   self.field_list
        return context
    
class SchoolUpdateView(LoginRequiredMixin, UpdateView):
    model = School
    template_name_suffix = '_form'
    form_class = SchoolForm
    success_url = reverse_lazy('school-list')
    

    def get_context_data(self, **kwargs):
        context = super(SchoolUpdateView, self).get_context_data(**kwargs)
        context['main_page_title'] = 'Update School Info'
        context['panel_name'] = 'School'
        context['panel_title'] = 'Update School Info'
        return context

class SchoolDeleteView(LoginRequiredMixin, DeleteView):
    model = School
    template_name_suffix = '_delete'
    success_url = reverse_lazy('school-list')

    def get_context_data(self, **kwargs):
        context = super(SchoolDeleteView, self).get_context_data(**kwargs)
        context['main_page_title'] = 'School Delete Confirmation'
        context['panel_name'] = 'School'
        context['panel_title'] = 'Delete School'
        return context