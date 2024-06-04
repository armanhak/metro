from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (PassengerViewSet, RequestViewSet,
                    EmployeeViewSet, WorkScheduleViewSet,
                    register_passenger, register_request,
                    register_employee, index)

router = DefaultRouter()
router.register(r'passengers', PassengerViewSet)
router.register(r'requests', RequestViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'work_schedules', WorkScheduleViewSet)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', index, name='index'),
    path('register_passenger/', register_passenger, name='register_passenger'),
    path('register_request/', register_request, name='register_request'),
    path('register_employee/', register_employee, name='register_employee'),
    path('api/', include(router.urls)),
]


# urlpatterns += [
#     path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
# ]