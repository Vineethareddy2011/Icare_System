
from django.contrib import admin
from django.urls import path,include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
   
]
from django.conf.urls.i18n import set_language
from django.conf.urls.i18n import i18n_patterns
urlpatterns += i18n_patterns(
    path('set_language/', set_language, name='set_language'),
    # Your other internationalized URL patterns go here
) 




