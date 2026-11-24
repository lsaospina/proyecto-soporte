from django.urls import path

from apps.dashboard.views import DashboardResumenView

urlpatterns = [
    path("dashboard/resumen/", DashboardResumenView.as_view(), name="dashboard-resumen"),
]
