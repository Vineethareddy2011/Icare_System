from django.contrib import admin
from django.urls import path,include,re_path
from . import views



urlpatterns = [
    path('',views.home, name='home'),
    path('login',views.loginPage, name='login'),   
    path('register/', views.registerPage, name="register"),
    path('logout/', views.logoutUser, name='logout'),
    path('patients_list/<slug:slug>', views.patients_list_view, name='viewpatients'),
    path('viewperm/', views.view_permissions, name='permit'),
    path('search/', views.SearchPatientsView.as_view(), name='SearchPatients'),
    path('search_user/', views.SearchUserView.as_view(), name='SearchUsers'),
    path('patient/create/', views.create_Patient_view, name='createPatient'),
    path('patient/edit/<str:pk>/', views.update_Patient_view, name='editPatient'),
    path('patient/<str:pk>/', views.patient_assign, name='assignPatient'),
    path('patient/delete/<str:pk>/', views.Patient_inactive_view, name='deletePatient'),
    path('patient/profile/<str:pk>/', views.Patient_profile_view, name='patientprofile'),
    path('patient/profile/update/<str:pk>/', views.updatepatientprofileview, name='updatePatientprofile'),
    path('patient/serve/<str:pk>/', views.serve_patient, name='servePatient'),
    path('patient/unserve/<str:pk>/', views.unassign_patient, name='unservePatient'),
    path('patient/visit/<str:pk>/', views.add_visit, name='addVisit'),
    path('users/list/', views.users_list_view, name='userslist'),
    path('user/create/', views.create_user_view, name='createuser'),
    path('user/edit/<str:pk>/', views.update_user_view, name='edituser'),
    path('user/profile/<str:pk>/', views.user_profile_view, name='userprofile'),
    path('user/delete/<str:pk>/', views.user_inactive_view, name='deleteuser'),
    path('report/create/<str:pk>/', views.report_create, name='createreport'),
    path('report/list/', views.report_list_view, name='reportlist'),
    path('viewreport/<str:pk>/', views.view_report, name='viewreport'),
    path('pdf_view/<str:pk>/',views.ViewPDF.as_view(),name='pdf_view'),
    re_path(r"pdf/download/(?P<pk>[\w-]+)/$", views.download_pdf, name='download_pdf'),
    path('pdf_Download/<str:pk>/',views.DownloadPDF.as_view(),name='pdf_download'),
    path('list_doctor/<str:pk>',views.doctors_list_view,name='list_doctors'),
    path('doctor/<patient_id>/<str:user_id>', views.assigndoctor,name='assigndoctor')
]
