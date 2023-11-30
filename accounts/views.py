from rest_framework import generics, permissions
from .serializers import UserRegistrationSerializer,LoginSerializer,UserSerializer,UserEditSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import login
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .models import User
from .premisson import IsUserOrReadOnly
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.authentication import TokenAuthentication

#CreateAPIViewを使う理由は作成に特化してるから(別にAPIViewでもいい)
class UserRegistrationView(generics.CreateAPIView):
    # シリアライザの指定
    serializer_class = UserRegistrationSerializer
    
    def post(self,request, *args, **kwargs):
        # 取得したデーターをシリアライザに渡す
        serializer = self.get_serializer(data=request.data)
        # 要件が満たされているかどうかを検証する
        # パラメータが設定されているので、raise_exception=Trueを指定する
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({
                "user": UserRegistrationSerializer(user).data,
                "message": "ユーザー登録が完了しました!"
            },status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# ログイン用のAPIView
class LoginAPIView(APIView):
    def post(self,request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # ログイン処理
            user = serializer.validated_data['user']
            # Djangoの login 関数を使って、ユーザーをログインさせます。
            # これにより、セッションが開始され、ユーザーは認証済みとして扱われる
            login(request, user)
            
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({"message": "ログインが成功しました！", 
                            'token': token.key,
                            'username': user.username},
                            status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#ログアウト用のAPIView
class LogoutAPIView(APIView):
    # このビューがトークン認証を使用し、認証済みのユーザーのみアクセスできるようにします
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # トークン削除
        request.auth.delete()
        return Response({"message":"ログアウトしました"},status=status.HTTP_200_OK)
    
# ユーザー情報取得用のAPIView
class UserDetailView(APIView):
    #　認証確認
    permission_classes = [IsAuthenticated]
    
    def get(self,request,username=None):
        # ユーザー名が指定されていない、または現在のユーザーのユーザー名の場合
        if username is None or username == request.user.username:
            user = request.user
        else:
            # 他のユーザーを取得
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"message": "ユーザーが見つかりませんでした。"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
# ユーザー情報更新用のAPIView
# フロントでPATCHメソッドを使って送信させる
class UserEditView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserEditSerializer

    # オブジェクトレベルの権限で、ユーザーが自分自身の情報のみ更新できるようにする。
    # 読み取りは全ユーザーに許可する。
    permission_classes = [IsUserOrReadOnly]
    
    def get_object(self):
        # URLからuseridを取得
        user = self.request.user

        # リクエストユーザーが対象のユーザーでない場合はPermissionDeniedエラーを発生させる
        if self.request.user != user:
            raise PermissionDenied("You do not have permission to update this user's profile.")

        return user
    
    
# User削除用のAPIView
class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        # オブジェクトを取得して削除
        obj = self.get_object()
        obj.delete()

        # カスタムレスポンスを返す
        return Response({"message": "ユーザーを削除しました！"}, 
                        status=status.HTTP_204_NO_CONTENT)