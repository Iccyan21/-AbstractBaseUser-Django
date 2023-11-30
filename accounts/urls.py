from django.urls import path
from .views import UserRegistrationView, LoginAPIView, UserDetailView,UserEditView,LogoutAPIView,UserDeleteView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'), #ユーザー登録
    path('login/', LoginAPIView.as_view(), name='login'), #ログイン
    path('profile/',UserDetailView.as_view(),name='detail'), #ユーザー情報取得
    path('profile/edit/',UserEditView.as_view(),name='update'), #ユーザー情報更新
    path('logout/',LogoutAPIView.as_view(),name='logout'), #ログアウト
    path('delete/',UserDeleteView.as_view(),name='delete'), #ユーザー削除
]

