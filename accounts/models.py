from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
# 完全にランダムなUUID
# セキュリティ的なランダム性を必要とする用途に適している
from uuid import uuid4

class UserManager(BaseUserManager):
    # 通常のユーザーを作成
    # どの値作成する時に必要かを指定
    # =Noneは任意の引数なんで記入しなくても良い
    def create_user(self, username,email,password,**extra_fields):     
        # 記入ミスをチェック
        if not username:
            raise ValueError('UserIDを入力してください')
        
        
        if not email:
            raise ValueError('メールアドレスを入力してください')
        
        if not password:
            raise ValueError('パスワードを入力してください')
        
        # Emailを正規化
        email = self.normalize_email(email)
        # モデルインスタンスを作成
        user = self.model(
            username = username,
            email = email,
            # ここでこれを返さないと謎のエラーでsupercreateuserがつくれない
            **extra_fields  
        )
        # パスワードをハッシュ化
        user.set_password(password)
        # ユーザーを保存
        user.save(using=self._db)
        return user
    
    # スーパーユーザーを作成
    # extra_fieldsは、ユーザーを作成する際に追加で設定できる属性の辞書を指します。
    def create_superuser(self, username, email,password,**extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        # createuserを呼び出しているため同じ値が必要
        return self.create_user(username,email,password,**extra_fields)
    
class User(AbstractBaseUser,PermissionsMixin):
    # usernameをユーザーIDとして使用するため、英数字のみを許可するバリデータを設定
    # ユーザー名が英字（大文字・小文字）および数字のみで構成されているかをチェック
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9]*$',  # 英数字のみを許可する正規表現
        message="ユーザー名は英数字のみで構成してください。"
    )
    # blank=Trueは空欄でも良いという意味
    username = models.CharField(max_length=20,unique=True,validators=[username_validator],blank=False) 
    email = models.EmailField(unique=True,blank=False)
    nickname = models.CharField(max_length=20,blank=False)
    coment = models.CharField(max_length=100,blank=True)
    # ログインしているかどうか
    is_active = models.BooleanField(default=True)
    # 管理サイトにアクセスできるかどうか
    # デフォルトは権限無し
    is_staff = models.BooleanField(default=False)
    # ユーザー作成やスーパーユーザー作成などのカスタムロジックを実装
    objects = UserManager()
    # ログインする時にはusername(userid)を使用
    USERNAME_FIELD = 'username'
    # 管理コマンドを使用してスーパーユーザーを作成する際に必要とされるフィールド
    # 特にないので空のリストを指定
    REQUIRED_FIELDS = ['email']
    
    
    # 管理者などで区別がつきやすいようにusernameで表示
    def __str__(self):
        return self.username
