import base64
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ApplicationForm
from .odoo_utils import fetch_odoo_jobs, create_odoo_application, get_odoo_connection
from .models import Application, Job
from django.db import connection

def job_list(request):
    search = request.GET.get('search', "")
    page_number = request.GET.get('page', 1)
    offset = (page_number - 1) * 12
    
    jobs = fetch_odoo_jobs(search, offset=offset, limit=12)
    
    if not jobs:
        messages.warning(request, "No jobs found in Odoo. Displaying local jobs. Check Odoo configuration and server console for details.")
        jobs = Job.objects.filter(Status='Active').order_by('-id')  # Sort by id descending
        if search:
            jobs = jobs.filter(Q(job_title__icontains=search) | Q(job_description__icontains=search))
        jobs = jobs.values('id', 'job_title', 'job_description', 'job_deadline', 'location', 'level')
        for job in jobs:
            job['name'] = job['job_title']
            job['job_description'] = job.get('job_description', '')
            job['career_level'] = job.get('level', 'Not Specified')
            job['cgpa_requirement'] = 0.0
            job['date_to'] = job['job_deadline']
            job['address_id'] = False
    
    for job in jobs:
        job['job_title'] = job['name']
        job['job_description'] = job.get('job_description', '')
        job['job_deadline'] = job.get('date_to', '')
        job['location'] = job['address_id'][1] if job.get('address_id') and isinstance(job['address_id'], (list, tuple)) else job.get('location', 'Remote')
        job['Status'] = job.get('Status', 'Active' if job.get('is_published', True) else 'Closed')
        job['career_level'] = job.get('career_level', 'Not Specified')
        job['cgpa_requirement'] = job.get('cgpa_requirement', 0.0)

    paginator = Paginator(jobs, 12)
    page_obj = paginator.get_page(page_number)

    return render(request, 'front/vacancy.html', {
        'jobs': page_obj.object_list,
        'page_obj': page_obj,
        'search': search,
        'page_title': 'Vacancies',
        'page_subtitle': 'Explore Our Current Job Openings',
        'announcement_page': True
    })

class jobs_apply(View):
    def _fetch_job(self, job_id):
        jobs = fetch_odoo_jobs()
        job = next((j for j in jobs if j['id'] == job_id), None)
        if not job:
            try:
                local_job = Job.objects.get(id=job_id, Status='Active')
                job = {
                    'id': local_job.id,
                    'name': local_job.job_title,
                    'job_title': local_job.job_title,
                    'job_description': local_job.job_description,
                    'date_to': local_job.job_deadline,
                    'location': local_job.location,
                    'Status': local_job.Status,
                    'career_level': local_job.level,
                    'cgpa_requirement': 0.0,
                    'address_id': False,
                    'company_id': False,
                    'department_id': False,
                }
            except Job.DoesNotExist:
                messages.error(self.request, "Job not found.")
                return redirect('job_list')
        else:
            job['Status'] = job.get('Status', 'Active' if job.get('is_published', True) else 'Closed')
        
        form = ApplicationForm()
        
        return render(
            self.request, 
            'front/vacancy_apply.html', 
            {'form': form,
             'job': job,
             'page_title': 'Apply for Vacancy',
             'page_subtitle': 'Fill in the details to apply for the vacancy',
             'announcement_page': True
        })
    
    def get(self, request, *args, **kwargs):
        job_id = self.kwargs['pk']
        return self._fetch_job(job_id)

    def post(self, *args, **kwargs):
        job_id = self.kwargs['pk']
        job = self._fetch_job(job_id)
        if not job:
            messages.error(self.request, "Job not found.")
            return redirect('job_list')

        form = ApplicationForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            cgpa = form.cleaned_data.get('cgpa_requirement', 0.0) or 0.0
            cgpa_requirement = job.get('cgpa_requirement', 0.0) or 0.0

            # Perform CGPA validation in Django
            if cgpa < cgpa_requirement:
                error_msg = f"Your CGPA ({cgpa}) does not meet the minimum requirement of {cgpa_requirement} for the position '{job['job_title']}'."
                messages.error(self.request, error_msg)
                return render(self.request, 'front/vacancy_apply.html', {
                    'form': form,
                    'job': job,
                    'job_id': job_id,
                    'debug': True
                })

            vals = {
                'partner_name': form.cleaned_data['partner_name'],
                'email_from': form.cleaned_data['email_from'],
                'partner_phone': form.cleaned_data['partner_phone'] or '',
                'cgpa_requirement': cgpa,
                'job_id': job_id,
                'linkedin_profile': form.cleaned_data.get('linkedin_profile', ''),
                'experience': form.cleaned_data.get('experience', 0),
            }

            if form.cleaned_data.get('attachment_ids'):
                cv_file = form.cleaned_data['attachment_ids']
                vals['cv_filename'] = cv_file.name
                vals['cv_data'] = base64.b64encode(cv_file.read()).decode('utf-8')

            is_local_job = job.get('Status') == 'Active'
            company_id = None
            if not is_local_job:
                try:
                    models, db, uid, password = get_odoo_connection()
                    job_exists = models.execute_kw(db, uid, password, 'hr.job', 'search',
                                                  [[('id', '=', job_id), ('is_published', '=', True), ('website_published', '=', True)]])
                    if not job_exists:
                        raise Exception(f"Job ID {job_id} does not exist or is not published in Odoo.")
                    job_data = models.execute_kw(db, uid, password, 'hr.job', 'read',
                                                [job_id, ['name', 'company_id']])
                    if not job_data[0].get('company_id'):
                        raise Exception(f"Job ID {job_id} has no valid company_id in Odoo.")
                    company_id = job_data[0]['company_id'][0]
                    vals['company_id'] = company_id
                except Exception as e:
                    messages.error(self.request, f"Error validating job: {str(e)}")
                    return redirect('job_list')

            try:
                # Log Application model fields
                from django.db.models import Field
                application_fields = [f.name for f in Application._meta.get_fields() if isinstance(f, Field)]

                # Log database schema
                with connection.cursor() as cursor:
                    cursor.execute("DESCRIBE vacancies_application")
                    db_columns = [row[0] for row in cursor.fetchall()]

                if not is_local_job:
                    create_odoo_application(vals)

                # Verify Application record creation
                application = Application.objects.create(
                    partner_name=vals['partner_name'],
                    email_from=vals['email_from'],
                    partner_phone=vals['partner_phone'],
                    cgpa_requirement=vals['cgpa_requirement'],
                    experience=vals['experience'],
                    job_odoo_id=job_id,
                    attachment_ids=form.cleaned_data.get('attachment_ids'),
                    linkedin_profile=vals['linkedin_profile'],
                )

                messages.success(self.request, "Applied Successfully.")
                return redirect('job_list')
            except Exception as e:
                messages.error(self.request, f"Error: {str(e)}")
                return render(self.request, 'front/vacancy_apply.html', {
                    'form': form,
                    'job': job,
                    'job_id': job_id,
                    'debug': True
                })
        else:
            messages.error(self.request, f"Invalid form data: {form.errors.as_text()}")
            return render(self.request, 'front/vacancy_apply.html', {
                'form': form,
                'job': job,
                'job_id': job_id,
                'debug': True
            })

def application_list(request):
    search = request.GET.get('search', None)
    min_cgpa = request.GET.get('cgpa_requirement', None)
    min_experience = request.GET.get('min_experience')

    filters = Q()
    if search:
        filters &= (Q(partner_name__icontains=search) | Q(email_from__icontains=search))
    if min_cgpa:
        try:
            filters &= Q(cgpa_requirement__gte=float(min_cgpa))
        except ValueError:
            pass
    if min_experience:
        try:
            filters &= Q(experience__gte=int(min_experience))
        except ValueError:
            pass

    applications = Application.objects.filter(filters)
    return render(request, 'front/applied_jobs_list.html', {
        'applications': applications,
        'search': search,
        'min_cgpa': min_cgpa,
        'min_experience': min_experience
    })