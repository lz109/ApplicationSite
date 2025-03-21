from django.urls import path 
from .views import home, signup, signin, signout, dashboard, admin_dashboard, officer_dashboard, view_profile, update_candidate_status, send_message, message_page
from .views import create_event, invite_candidate_to_event, edit_profile, add_officer, remove_officer, upload_document, add_candidate, candidate_profile, edit_candidate
from .views import send_message_to_user, statistics_view
urlpatterns = [ 
    path("", home, name="home"), 
    path("signup/", signup, name="signup"),
    path("signin/", signin, name="signin"),
    path("signout/", signout, name="signout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("admin_dashboard/", admin_dashboard, name="admin_dashboard"),
    path("officer_dashboard/", officer_dashboard, name="officer_dashboard"),
    path("profile/", view_profile, name="view_profile"),

    path("send-message/", send_message, name="send_message"),
    path("messages/", message_page, name="messages_page"),
    path("create-event/", create_event, name="create_event"),
    path("invite-candidate-to-event/", invite_candidate_to_event, name="invite_candidate_to_event"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/add-officer/', add_officer, name='add_officer'),
    path('admin-dashboard/remove-officer/<int:user_id>/', remove_officer, name='remove_officer'),
    path("update-candidate/<int:candidate_id>/", update_candidate_status, name="update_candidate_status"),
    path("upload-document/", upload_document, name="upload_document"),
    path("add_candidate/", add_candidate, name="add_candidate"),
    path('candidate/<int:candidate_id>/', candidate_profile, name='candidate_profile'),
    path('candidate/<int:candidate_id>/edit/', edit_candidate, name='edit_candidate'),  # New Edit Page
    path('send-message-to-user/', send_message_to_user, name='send_message_to_user'),
    path("statistics/", statistics_view, name="statistics"),
]
