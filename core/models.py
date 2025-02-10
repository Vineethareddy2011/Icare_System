from multiprocessing.sharedctypes import Value
from django.db import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin,User,Permission
from .utils import create_new_ref_number

GENDER_TYPES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

USER_ROLES = (
    ('OfficeAdmin', 'OfficeAdmin'),
    ('Doctor', 'Doctor'),
    ('Nurse', 'Nurse')
)

BLOOD_TYPES = (
    ('A','A'),
    ('B','B'),
    ('AB','AB'),
    ('O','O')
)

SERVICE_STATUS=(
    ('Served','Served'),
    ('Inservice','Inservice'),
    ('Waiting','Waiting')
)



RECEIPT_TYPES = (
    ('EntranceFee', 'EntranceFee'),
    ('MembershipFee', 'MembershipFee'),
    ('BookFee', 'BookFee'),
    ('LoanProcessingFee', 'LoanProcessingFee'),
    ('AdditionalSavings', 'AdditionalSavings'),
    ('LoanDeposit', 'LoanDeposit'),
)

FD_RD_STATUS = (
    ('Opened', 'Opened'),
    ('Paid', 'Paid'),
    ('Closed', 'Closed'),
)




class UserManager(BaseUserManager):
    def create_superuser(self, username, first_name, email, password, **other_fields):
        other_fields.setdefault('is_admin', True)
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        if other_fields.get('is_staff') is not True:
            raise ValueError('SuperUser must be assigned to is_staff=True')
        if other_fields.get('is_admin') is not True:
            raise ValueError('SuperUser must be assigned to is_admin=True')
        return self.create_user(username, first_name, email, password, **other_fields)

    def create_user(self, username,first_name, email, password,**other_fields):
        if not username:
            raise ValueError('Users must have an username')
        # Save the user
        email = self.normalize_email(email)
        user = self.model(username=username,email=email,first_name=first_name,**other_fields)
        user.set_password(password)
        user.is_staff = True
        user.save()
        return user

    


class User(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True)
    user_roles = models.CharField(choices=USER_ROLES, max_length=20)
    date_of_birth = models.DateField(default='2000-01-01', null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    country = models.CharField(max_length=50, null=True)
    county = models.CharField(max_length=50, null=True)
    subcounty = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    area = models.CharField(max_length=150, null=True)
    mobile = models.CharField(max_length=10, default='0', null=True)
    pincode = models.CharField(default='', max_length=10, null=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name='user_permissions', blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS=['email','first_name']

    def __unicode__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_admin:
            return True
        # return _user_has_perm(self, perm, obj)
        else:
            try:
                user_perm = self.user_permissions.get(codename=perm)
            except ObjectDoesNotExist:
                user_perm = False

            return bool(user_perm)

    class Meta:
        permissions = (
            ("OfficeAdmin","Can manage all users accounts."),
            ("Add_user","Can add user accounts."),
            ("edit_patients","Can edit patient accounts."),
            ("view_patients","Can view patient accounts."),
            ("manage_patients","Can manage patient accounts."),
        )



class Patient(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    national_id= models.PositiveIntegerField(default=0,unique=True)
    email = models.EmailField(max_length=255, null=True)
    created_by= models.ForeignKey(User,on_delete=models.PROTECT,related_name='created_by')
    patient_id = models.CharField(max_length=50, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(choices=GENDER_TYPES, max_length=10)
    blood_type = models.CharField(choices=BLOOD_TYPES, max_length=5)
    occupation = models.CharField(max_length=200)
    country = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    subcounty = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    area = models.CharField(max_length=150)
    mobile = models.CharField(max_length=20, default=True, null=True)
    pincode = models.CharField(max_length=20, default=True, null=True)
    photo = models.ImageField(upload_to=settings.PHOTO_PATH, null=True)
    medcare=models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(choices=SERVICE_STATUS, max_length=50, default="UnAssigned", null=True)
    bookfee_amount = models.DecimalField(max_digits=19, decimal_places=6, default=0)

    def __unicode__(self):
        return self.first_name + ' ' + self.last_name

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
    def __str__(self):
        return f"{self.first_name},{self.last_name}"
    
    @property
    def get_visits(self):
        self.vis=Visits()
        if self.vis.patient == self:
            return self.vis
    @property
    def get_documents(self):
        self.doc=Documents()
        if self.doc.patient == self:
            return self.doc

class Visits(models.Model):
    visit_id = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey(Patient, to_field='patient_id', null=True, blank=True,on_delete=models.PROTECT)
    assigned_to= models.ManyToManyField(User,blank=True)
    visit_date = models.DateField(default='2020-01-01', null=True)
    visit_time = models.TimeField(auto_now_add=True)
    visit_status=models.CharField(choices=SERVICE_STATUS, max_length=50, default="UnAssigned", null=True)
    admission_date = models.DateField(default='2020-01-01', null=True)
    release_date = models.DateField(default='2020-01-01', null=True)

class Documents(models.Model):
    date = models.DateField(auto_now_add=True)
    doc_id = models.CharField(max_length=50,editable=False, unique=True,default=create_new_ref_number)
    patient = models.ForeignKey(Patient, to_field='patient_id', null=True, blank=True,on_delete=models.PROTECT)
    staff = models.ForeignKey(User, null=True, blank=True,on_delete=models.PROTECT)
    upload = models.FileField(upload_to='uploads/')
    def __unicode__(self):
        return self.voucher_number

class Report(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    blood_type = models.CharField(choices=BLOOD_TYPES, max_length=5)
    medcare=models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=20, default=True, null=True)
    doc_id = models.ForeignKey(Documents, null=True, blank=True,on_delete=models.PROTECT)   
    date = models.DateField(auto_now_add=True)
    patient = models.ForeignKey(Patient, to_field='patient_id', null=True, blank=True,on_delete=models.PROTECT)
    staff = models.ForeignKey(User, to_field='username', null=True, blank=True,on_delete=models.PROTECT)
    diagnosis=models.TextField(default='No Diagnosis')
    medical_history=models.TextField(default='No medical history')
    