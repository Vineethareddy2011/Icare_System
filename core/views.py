# from os import PRIO_USER
import decimal
import time
import pdfkit
from .models import  Patient, User, USER_ROLES,SERVICE_STATUS,Visits,Documents,BLOOD_TYPES,Report
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.contrib import messages
from django.views.generic import ListView,DetailView
from django.views.generic.base import View,ContextMixin
from django.conf import settings
from django.db.models import Sum, Q
from django.contrib.auth.models import Permission, ContentType
from django.urls import reverse
from .utils import create_new_ref_number,create_new_med_number
from django.template.loader import get_template
from django.template import Context, Template
from io import BytesIO
from xhtml2pdf import pisa

from.forms import (PatientForm, UserForm,ReportForm,MyForm,
                   ChangePasswordForm,  UpdatePatientProfileForm)


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist.')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist.')
    context = {'page': page}
    return render(request, 'login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    page = 'register'
    form = PatientForm()
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.created_by = 'SELF'
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    return render(request, 'login.html', {'form': form})

from django.conf import settings
@login_required(login_url='login')
def home(request):
    print(settings.LANGUAGES)
    if request.user.is_authenticated:
        user = request.user
        visit=Visits.objects.filter(assigned_to=request.user).values()
        print(Patient.get_visits)
        if user.is_active and user.is_staff:
            Served_patients = Patient.objects.filter(status='Served', visits__assigned_to=request.user).count()
            Inservice_patients = Patient.objects.filter(
                status='Inservice', visits__assigned_to=request.user).count()
            Waiting_patients = Patient.objects.filter(
                status='Waiting',visits__assigned_to=request.user).count()
            Patients_count = Patient.objects.filter(
                visits__assigned_to=request.user).count()
            Patients = Patient.objects.filter(visits__assigned_to=request.user)
            context = {"user": user,
                       "Patients": Patients,
                       "Patients_count": Patients_count,
                       "Served_patients": Served_patients,
                       "Inservice_patients": Inservice_patients,
                       "Waiting_patients": Waiting_patients,
                       'LANGUAGES': settings.LANGUAGES,
                       }
            return render(request, "admin.html", context)
        
        elif user.is_active and user.is_staff and user.user_roles == 'OfficeAdmin':
            Served_patients = Patient.objects.filter(
                status='Served').count()
            Inservice_patients = Patient.objects.filter(
                status='Inservice').count()
            Waiting_patients = Patient.objects.filter(
                status='Waiting').count()
            staff_count = User.objects.count()
            Patients_count = Patient.objects.all().count()
            Patients = Patient.objects.all()
            context = {"user": user,
                       "Patients": Patients,
                       "Patients_count": Patients_count,
                       "staff_count": staff_count,
                       "Served_patients": Served_patients,
                       "Inservice_patients": Inservice_patients,
                       "Waiting_patients": Waiting_patients
                       }
            return render(request, "admin.html", context)
        else:
            messages.error(request, 'user does not exist.')
        #receipts_list = Receipts.objects.all().order_by("-id")
        #payments_list = Payments.objects.all().order_by("-id")
        # "receipts": receipts_list,
        # "payments": payments_list,
        return render(request, "admin.html", context)
    return render(request, "login.html")


def logoutUser(request):
    logout(request)
    return redirect('home')


####----- Patient MANAGEMENT -----####
@login_required(login_url='login')
def create_Patient_view(request):
    form = PatientForm()
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            #print(patient.cleaned_data)
            patient.created_by = request.user
            patient.save()
            visit=Visits()
            visit.visit_id = create_new_ref_number()
            visit.patient=patient
            visit.visit_status='UnAssigned'
            curr_date = time.strftime("%Y-%m-%d", time.localtime())
            visit.visit_date=curr_date
            visit.save()
            return HttpResponseRedirect(reverse("patientprofile", kwargs={"pk":patient.id}))
        else:
            return JsonResponse({"error": True, "errors": form.errors})
    return render(request, "patient/create.html",{"blood_types":BLOOD_TYPES})

@login_required(login_url='login')
def Patient_profile_view(request, pk):
    patient = get_object_or_404(Patient, id=pk)
    visits = Visits.objects.filter(patient=patient)
    visits_count = Visits.objects.filter(patient=patient).count()
    visit=Visits.objects.filter(patient=patient).latest('visit_time')
    varray = visit.assigned_to.all()
    context = {
        'Patient': patient,
        'visits': visits,
        'varray' : varray,
        'visits_count': visits_count
    }
    return render(request, "patient/profile.html", context)

@login_required(login_url='login')
def update_Patient_view(request, pk):
    form = PatientForm()
    patient_obj = get_object_or_404(Patient, id=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient_obj)
        if form.is_valid():
            patient = form.save()
            return HttpResponseRedirect(reverse("patientprofile", kwargs={"pk": patient.id}))
        else:
            return JsonResponse({"error": True, "errors": form.errors})
    return render(request, "patient/edit.html", {'patient': patient_obj})

@login_required(login_url='login')
def updatepatientprofileview(request, pk):
    patient_obj = get_object_or_404(Patient, pk=pk)
    form = UpdatePatientProfileForm(instance=patient_obj)
    if request.method == 'POST':
        form = UpdatePatientProfileForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save(commit=False)
            patient_obj.photo = patient.photo
            patient_obj.save()
            return HttpResponseRedirect(reverse("patientprofile", kwargs={"pk": patient_obj.id}))
        else:
            data = {"error": True, "errors": form.errors}
            return JsonResponse(data)

    photo = str(patient_obj.photo).split('/')[-1] if patient_obj.photo else None

    return render(request, "patient/update-profile.html", {'patient': patient_obj,
                                                          'form': form, 'photo': photo})

#@login_required(login_url='login')
def patients_list_view(request,slug):
    if request.user.is_authenticated:
        user = request.user
        #visit=Visits.objects.filter(assigned_to=request.user)
        if user.is_active and user.is_staff:
            if slug=='0':
                Patient_list = Patient.objects.all()
            elif slug=='a':
                Patient_list = Patient.objects.filter(visits__assigned_to=request.user)
            elif slug=='Waiting':
                Patient_list = Patient.objects.filter(visits__assigned_to=request.user, status='Waiting')
            elif slug=='Inservice':
                Patient_list = Patient.objects.filter(visits__assigned_to=request.user, status='Inservice')
            elif slug=='Served':
                Patient_list = Patient.objects.filter(visits__assigned_to=request.user, status='Served')             
            return render(request, "Patients_list.html", {'Patient_list': Patient_list})
        else:
            Patient_list = None
    return render(request, "Patients_list.html", {'Patient_list': Patient_list})

class SearchPatientsView(ListView):
    model = Patient
    template_name = "Patients_list.html"
    def get_queryset(self):  # new
        query = self.request.GET.get("q")
        Patient_list = Patient.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
        return Patient_list

@login_required(login_url='login')
def Patient_inactive_view(request, pk):
    patient = get_object_or_404(Patient, id=pk)
    if patient.is_active:
        count = 0
        docs = Documents.objects.filter(patient=patient)
        if docs:
            for doc in docs:
                if count == docs.count():
                    patient.is_active = False
                    patient.save()
                    return HttpResponseRedirect(reverse("patientprofile"))
                else:
                    messages.error(
                        request, "Oops! Patient has a documents related to them, Unable to delete.")
        else:
            patient.is_active = False
            patient.save()
    return HttpResponseRedirect(reverse("viewPatient"))

def patient_assign(request,pk):
    patient = get_object_or_404(Patient, id=pk)
    Patient_list = Patient.objects.all()
    if patient.status == 'UnAssigned':
        patient.status='Waiting'
        patient.save()
        visit=Visits.objects.get(patient=patient, visit_status='UnAssigned')
        visit.assigned_to.add(request.user)
        visit.visit_status='Waiting'
        visit.save()    
    elif patient.status == 'Waiting':
        visit=Visits.objects.get(patient=patient, visit_status='Waiting')
        visit.assigned_to.add(request.user)
    elif patient.status == 'Inservice':
        messages.error(request, "This patient is waiting service")
    else:
        messages.error(request, "This patient is served")
    return render(request, "Patients_list.html", {'Patient_list': Patient_list})

def serve_patient(request,pk):
    patient = get_object_or_404(Patient, id=pk)
    if patient.status == 'Waiting':
        patient.status='Inservice'
        patient.save()
        visit=Visits.objects.get(patient=patient, visit_status='Waiting')
        visit.visit_status='Inservice'
        visit.save()
    elif patient.status == 'Inservice':
        patient.status='Served'
        patient.save()
        visit=Visits.objects.get(patient=patient, visit_status='Inservice')
        visit.assigned_to.clear()
        visit.visit_status='Served'
        visit.save()
    return HttpResponseRedirect(reverse("patientprofile", kwargs={"pk":patient.id}))

def unassign_patient(request,pk):
    patient = get_object_or_404(Patient, id=pk)
    if patient.status == 'Waiting':
        visit=Visits.objects.get(patient=patient, visit_status='Waiting')
        varray = visit.assigned_to.all()
        if request.user in varray and len(varray)==1:   
            patient.status = 'UnAssigned'
            patient.save()
            visit.assigned_to.remove(request.user)
            visit.visit_status='UnAssigned'
            visit.save()
        elif request.user in varray and len(varray)>1:
            visit.assigned_to.remove(request.user)
            visit.save()
    elif patient.status == 'Inservice':
        visit=Visits.objects.get(patient=patient, visit_status='Inservice')
        varray = visit.assigned_to.all()
        if request.user in varray and len(varray)==1:   
            patient.status = 'UnAssigned'
            patient.save()
            visit.assigned_to.remove(request.user)
            visit.visit_status='UnAssigned'
            visit.save()
        elif request.user in varray and len(varray)>1:
            visit.assigned_to.remove(request.user)
            visit.save()

    return HttpResponseRedirect(reverse("patientprofile", kwargs={"pk":patient.id}))

def add_visit(request,pk):
    patient = get_object_or_404(Patient, id=pk)
    patient.status='UnAssigned'
    patient.save()
    visit=Visits()
    visit.visit_id = create_new_ref_number()
    visit.visit_status='UnAssigned'   
    visit.patient=patient
    curr_date = time.strftime("%Y-%m-%d", time.localtime())
    visit.visit_date=curr_date
    visit.save()
    
    return HttpResponseRedirect(reverse("patientprofile", kwargs={"pk":patient.id}))

def doctors_list_view(request,pk):
    patient = get_object_or_404(Patient, id=pk)
    list_of_users = User.objects.filter(user_roles='Doctor')
    return render(request, "user/assign_doctor.html", {'list_of_users': list_of_users,'patient':patient.id})

def assigndoctor(request,patient_id,user_id):
    patient = get_object_or_404(Patient, id=patient_id)
    user=get_object_or_404(User, id=user_id)
    if patient.status == 'UnAssigned':
        patient.status='Waiting'
        patient.save()
        visit=Visits.objects.get(patient=patient, visit_status='UnAssigned')
        visit.assigned_to.add(user)
        visit.visit_status='Waiting'
        visit.save()    
    elif patient.status == 'Waiting':
        visit=Visits.objects.get(patient=patient, visit_status='Waiting')
        visit.assigned_to.add(user)
    elif patient.status == 'Inservice':
        messages.error(request, "This patient is waiting service")
    else:
        messages.error(request, "This patient is served")
    return HttpResponseRedirect(reverse("patientprofile", kwargs={"pk":patient.id}))

###-------------USER MANAGEMENT---------###

@login_required(login_url='login')
def create_user_view(request):
    contenttype = ContentType.objects.get_for_model(request.user)
    print(contenttype)
    permissions = Permission.objects.filter(content_type_id=contenttype, codename__in=[
                                            "OfficeAdmin", "edit_patients", "Add_user", "view_patients", "manage_patients"])
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            format = '%Y-%m-%d'
            user.date_of_birth = user.date_of_birth.strftime(format)
            user.save()
            if len(request.POST.getlist("user_permissions")):
                user.user_permissions.add(
                    *request.POST.getlist("user_permissions"))
            if request.POST.get("user_roles") == "OfficeAdmin":
                if not user.user_permissions.filter(id__in=request.POST.getlist("user_permissions")).exists():
                    user.user_permissions.add(
                        Permission.objects.get(codename="OfficeAdmin"))
            return HttpResponseRedirect(reverse("userprofile", kwargs={"pk": user.id}))
        else:
            return JsonResponse({"error": True, "errors": form.errors})

    return render(request, "user/create.html", {
        'form': form, 'userroles': USER_ROLES, 'permissions': permissions})

@login_required(login_url='login')
def update_user_view(request, pk):
    contenttype = ContentType.objects.get_for_model(request.user)
    permissions = Permission.objects.filter(content_type_id=contenttype, codename__in=[
                                            "OfficeAdmin", "edit_patients", "Add_user", "view_patients", "manage_patients"])
    form = UserForm()
    selected_user = User.objects.get(id=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=selected_user)
        if form.is_valid():
            if not (
               request.user.is_admin or request.user == selected_user or
               (
                   request.user.has_perm("OfficeAdmin") and
                   request.user.branch == selected_user.branch
               )):
                return JsonResponse({
                    "error": True,
                    "message": "You are unbale to Edit this staff details.",
                    "success_url": reverse('userslist')
                })
            else:
                user = form.save()
                user.user_permissions.clear()
                user.user_permissions.add(
                    *request.POST.getlist("user_permissions"))
                if request.POST.get("user_roles") == "OfficeAdmin":
                    if not user.user_permissions.filter(id__in=request.POST.getlist("user_permissions")).exists():
                        user.user_permissions.add(
                            Permission.objects.get(codename="OfficeAdmin"))

                return JsonResponse({
                    "error": False,
                    "success_url": reverse('OfficeAdmin', kwargs={"pk": user.id})
                })
        else:
            return JsonResponse({"error": True, "errors": form.errors})

    return render(request, "user/edit.html", {
        'form': form, 'userroles': USER_ROLES, 'permissions': permissions, 'selecteduser': selected_user})

@login_required(login_url='login')
def user_profile_view(request, pk):
    selecteduser = get_object_or_404(User, id=pk)
    return render(request, "user/profile.html", {'selecteduser': selecteduser})

@login_required(login_url='login')
def users_list_view(request):
    list_of_users = User.objects.filter(is_admin=0, is_active=1)
    return render(request, "user/list.html", {'list_of_users': list_of_users})

@login_required(login_url='login')
def user_inactive_view(request, pk):
    user = get_object_or_404(User, id=pk)
    if (request.user.is_admin or request.user.has_perm("OfficeAdmin")):
        if user.is_active and user.is_admin == False:
            user.delete()
        elif user.is_active and user.is_admin == True:
            user.is_active = False
            user.save()
        else:
            user.is_active = True
            user.save()
    return HttpResponseRedirect(reverse('userslist'))


class SearchUserView(ListView):
    model = User
    template_name = "user/list.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        user_list = User.objects.filter(
            Q(first_name__icontains=query) | Q(
                last_name__icontains=query) | Q(username__icontains=query)
        )
        return user_list

@login_required(login_url='login')
def view_permissions(request):
    permissions = Permission.objects.all()
    return render(request, "permissionn.html", {'permissions': permissions})

####---------REPORT----------####
def report_create(request,pk):
    patient = get_object_or_404(Patient, id=pk)
    staff = request.user.username
    curr_date = time.strftime("%Y-%m-%d", time.localtime())
    context={
        'patient':patient,
        'staff':staff,
        'curr_date':curr_date
    }
    form = ReportForm()
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report=form.save()
            return HttpResponseRedirect(reverse("viewreport", kwargs={"pk": report.id}))
        else:
            return JsonResponse({"error": True, "errors": form.errors})
    return render(request, "report/reportform.html", context)

def view_report(request, pk):
    report = get_object_or_404(Report, id=pk)
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse("pdf_view", kwargs={"pk": report.id}))
    return render(request, "report/viewreport.html", {'report': report,'pk':pk})

def render_to_pdf(template_src,context_dict={}):
    template = get_template(template_src)
    #context=Context(context_dict)
    html= template.render(context_dict)
    results=BytesIO()
    pdf =pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")),results)
    if not pdf.err:
        return HttpResponse(results.getvalue(),content_type='application/pdf')
    return None


class ViewPDF(View):
    def get(self,request,pk,*args,**kwargs):
        report=get_object_or_404(Report, id=pk)
        staff=report.staff
        date=report.date
        first_name=report.first_name
        last_name=report.last_name
        city=report.city
        blood_type=report.blood_type
        pincode= report.pincode
        medcare=report.medcare
        diagnosis=report.diagnosis
        medical_history=report.medical_history
        context={
            'staff':staff,
            'date':date,
            'first_name':first_name,
            'last_name':last_name,
            'city':city,
            'blood_type':blood_type,
            'pincode':pincode,
            'medcare':medcare,
            'diagnosis':diagnosis,
            'medical_history':medical_history}
        pdf = render_to_pdf('pdf_report.html',context)
        return HttpResponse(pdf,content_type='application/pdf')

def download_pdf(request,pk):
    report = Report.objects.get(id=pk)
    return HttpResponseRedirect(reverse("pdf_download", kwargs={"pk": report.id}))

class DownloadPDF(View):
    def get(self,request,pk,*args,**kwargs):
        report = Report.objects.get(id=pk)
        patient=Patient.objects.get(patient_id=report.patient)
        staff=report.staff
        date=report.date
        first_name=report.first_name
        last_name=report.last_name
        city=report.city
        blood_type=report.blood_type
        pincode= report.pincode
        medcare=report.medcare
        diagnosis=report.diagnosis
        medical_history=report.medical_history
        context={
            'staff':staff,
            'date':date,
            'first_name':first_name,
            'last_name':last_name,
            'city':city,
            'blood_type':blood_type,
            'pincode':pincode,
            'medcare':medcare,
            'diagnosis':diagnosis,
            'medical_history':medical_history}
        pdf = render_to_pdf('pdf_report.html',context)
        response =HttpResponse(pdf,content_type='application/pdf')
        filename="report-{0}-{1}".format(patient,report.date)
        content="attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    

@login_required(login_url='login')
def report_list_view(request):
    Report_list = Report.objects.all()
    return render(request, "report/report_list.html", {'Report_list': Report_list})

# ViewSets define the view behavior.
        #super(ReportView, self).get_context_data(pagesize='A4',title='Patient Report',**kwargs )
    
''' class MyPDF(PDFTemplateView):
    timee = time.localtime()
    filename = 'report-0'.format(timee)
    template_name = 'reportform.html'
    cmd_options = {
        'margin-top': 3,
    } ''' 
