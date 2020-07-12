from django.contrib import admin
from django.conf.urls import include, url
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from rest_framework.authtoken import views as authviews
from horologium import views

router = routers.DefaultRouter()
router.register(r'signup', views.SignUpViewSet, basename='signup')
router.register(r'users', views.UserViewSet, basename="users")
#router.register(r'groups', views.GroupViewSet, basename="groups")
router.register(r'timers', views.TimerViewSet, basename="timers")
timer_router = nested_routers.NestedSimpleRouter(router, 'timers', lookup='timer', trailing_slash=False)
timer_router.register(r'durations', views.DurationSubViewSet, basename='timers-durations')
router.register(r'durations', views.DurationViewSet, basename="durations")
router.register(r'countdowns', views.CountdownViewSet, basename="countdowns")
router.register(r'notes', views.NoteViewSet, basename="notes")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^token-auth/', authviews.obtain_auth_token),
    url(r'^api/(?P<version>(v1))/', include(timer_router.urls)),
    url(r'^api/(?P<version>(v1))/', include(router.urls)),
    url('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]