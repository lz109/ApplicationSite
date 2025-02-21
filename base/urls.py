from django.urls import path 
from .views import home, signup, signin, signout, dashboard, admin_dashboard, officer_dashboard, view_profile, update_profile
  
urlpatterns = [ 
    path("", home, name="home"), 
    path("signup/", signup, name="signup"),
    path("signin/", signin, name="signin"),
    path("signout/", signout, name="signout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("admin_dashboard/", admin_dashboard, name="admin_dashboard"),
    path("officer_dashboard/", officer_dashboard, name="officer_dashboard"),
    path("profile/", view_profile, name="view_profile"),
    path("profile/edit/", update_profile, name="update_profile"),
]