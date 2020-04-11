from django.urls import path

from.views import signup, ActivateUser, templateEmailSent, UserList, UserApp, ProfileAPI, newAccount, getBadget, Movement, newMovement, deleteMovement, disableStateAccount

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('activate/<str:uidb64>/<str:token>/', ActivateUser, name='activate'),
    path('emailsent/<str:username>/', templateEmailSent, name='emailsent'),
    path('listar/', UserList.as_view(), name="listar"),
    path('userapp/<pk>', UserApp, name="userapp"),
	path('api/', ProfileAPI.as_view(), name = "api"),
	path('api/<int:pk>', ProfileAPI.as_view(), name = "api"),
	path('newAccount/<pk>', newAccount, name = "newAccount"),
	path('getBadget/<int:pk>/<int:pk_user>', getBadget, name = "getBadget"),
	path('movement/<pk>', Movement, name = "movement"),
	path('newMovement/<pk_account>/<pk_balance>/<pk_user>', newMovement, name = "newMovement"),
	path('deleteMovement/<pk_account>/<pk_balance>/<pk_user>/<pk_movement>', deleteMovement, name = "deleteMovement"),
	path('disableStateAccount/<pk>/<account_number>/<creation_day>/<type_account>/<state_account>/<pk_user>', disableStateAccount, name = "disableStateAccount")
]