from django.urls import path 
from .views import home, signup, signin, dashboard, admin_dashboard, dashboard_data, view_profile, update_candidate_status
from .views import edit_profile, add_officer, remove_officer, add_candidate, candidate_profile, edit_candidate
from .views import SignUpAPIView, SignInAPIView, dashboard_data, upload_resume, statistics_api, profile_view, upload_photo
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test

from .views import dashboard_data, upload_resume, list_events_api
from .views import create_event_api, invite_candidates_api, list_candidates_api, officer_list, logout_view, list_message_recipients
from .views import MessageListCreateView, MessageMarkAsReadView
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import never_cache
# serve React at officer_dashboard
index_view = never_cache(TemplateView.as_view(template_name='index.html'))
urlpatterns = [
    path('', index_view),  # Catch-all
]

urlpatterns = [ 
    path("", home, name="home"), 
    path("api/signup/", SignUpAPIView.as_view(), name="api-signup"),
    path("api/signin/", SignInAPIView.as_view(), name="api-signin"),
    path("signup/", signup, name="signup"),
    path("signin/", signin, name="signin"),
    #path("signout/", signout, name="signout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("admin_dashboard/", admin_dashboard, name="admin_dashboard"),

    path("profile/", view_profile, name="view_profile"),

    # path("send-message/", send_message, name="send_message"),
    path('api/messages/', MessageListCreateView.as_view(), name='message-list'),
    path('api/messages/<int:pk>/mark_as_read/', MessageMarkAsReadView.as_view(), name='message-mark-read'),
    # path("create-event/", create_event, name="create_event"),
    # path("invite-candidate-to-event/", invite_candidate_to_event, name="invite_candidate_to_event"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/add-officer/', add_officer, name='add_officer'),
    path('admin-dashboard/remove-officer/<int:user_id>/', remove_officer, name='remove_officer'),
    path("update-candidate/<int:candidate_id>/", update_candidate_status, name="update_candidate_status"),
    #path("upload-document/", upload_document, name="upload_document"),
    #path("add_candidate/", add_candidate, name="add_candidate"),
    path('candidate/<int:candidate_id>/', candidate_profile, name='candidate_profile'),
    path('candidate/<int:candidate_id>/edit/', edit_candidate, name='edit_candidate'),  # New Edit Page
    #path('send-message-to-user/', send_message_to_user, name='send_message_to_user'),
    #path("statistics/", statistics_view, name="statistics"),
    path("api/statistics/", statistics_api, name="statistics_api"),

    #path("officer_dashboard/", officer_dashboard_view, name="officer_dashboard"),  # ⬅️ renders React
    path("api/dashboard/", dashboard_data, name="dashboard_data"),                 # ⬅️ still serve JSON
    path("api/upload_resume/", upload_resume, name="upload_resume"),
    path("api/add_candidate/", add_candidate, name="add_candidate"),
    path("api/events/", list_events_api, name="list_events_api"),
    path("api/create_event/", create_event_api, name="create_event_api"),
    path("api/invite_candidates/", invite_candidates_api, name="invite_candidates_api"),
    path("api/candidates/", list_candidates_api, name="list_candidates_api"),
    path("api/officers/", officer_list, name="officer-list"),
    path("api/profile/", profile_view),
    path("api/profile/upload-photo/", upload_photo),
    # urls.py
    path("api/logout/", logout_view, name="logout"),
    path("api/recipients/", list_message_recipients, name="list_message_recipients"),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
