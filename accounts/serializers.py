from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
import re
# カスタムユーザーモデルを使用している場合は、
# 取得するユーザーモデルを指定する必要があります。
User = get_user_model()

#　新規登録用のシリアライザ
# ModelSerializerはDjangoモデルをJSONに変換したり、
# JSONをモデルに変換したりするためのロジックを持っています。
class  UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    
    # シリアライザをカスタマイズ
    class Meta:
        model = User
        fields = ('username','email','password', 'password_confirm',)
        # パスワードを書き込み専用にしてレスポンスに含めないようにする
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    # シリアライザの値が有効かどうかを検証する
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "確認パスアードと一致しません"})
        return attrs
    
    # usernameに英数字以外が含まれていないかを検証する
    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9]*$', value):
            raise serializers.ValidationError("ユーザー名は英数字のみで構成してください。")
        return value
    
    # 残りのデーターをしようしてユーザーを作成する
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        # ここでModelsのcreate_userを呼び出している
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user
    
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
import re
# カスタムユーザーモデルを使用している場合は、
# 取得するユーザーモデルを指定する必要があります。
User = get_user_model()

#　新規登録用のシリアライザ

# ModelSerializerはDjangoモデルをJSONに変換したり、
# JSONをモデルに変換したりするためのロジックを持っています。
class  UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    
    # シリアライザをカスタマイズ
    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirm', 'displayname','email','context', 'profileImage', 'sports', 'position', 'job')
        # パスワードを書き込み専用にしてレスポンスに含めないようにする
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    # シリアライザの値が有効かどうかを検証する
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "確認パスアードと一致しません"})
        return attrs
    
    # usernameに英数字以外が含まれていないかを検証する
    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9]*$', value):
            raise serializers.ValidationError("ユーザー名は英数字のみで構成してください。")
        return value
    
    # 残りのデーターをしようしてユーザーを作成する
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        # ここでModelsのcreate_userを呼び出している
        user = User.objects.create_user(
            username=validated_data['username'],
            displayname=validated_data['displayname'],
            email=validated_data['email'],
            password=validated_data['password'],
            # ここは別になくてもいいので空文字を入れておく
            context=validated_data.get('context', ''),
            profileImage=validated_data.get('profileImage'),  # ここを変更
            sports=validated_data.get('sports', ''),
            position=validated_data.get('position', ''),
            job=validated_data.get('job', '')
        )
        return user
    
#　ログインシリアライザ
class LoginSerializer(serializers.Serializer):
    # username(userId)とpasswordを受け取る
    username = serializers.CharField() 
    #style={'input_type': 'password'}により、APIブラウザでパスワードフィールドがマスクされます。
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        # 両方定義されてるかどうかを検証する
        if username and password:
            #  Djangoの authenticate 関数を使用して、提供されたユーザー名とパスワードでユーザーを認証
            user = authenticate(request=self.context.get('request'),username=username, password=password)
            if not user:
                mag = '提供された認証情報ではログインできません。'
                raise serializers.ValidationError(mag, code='authorization')
            
        else:
            mag = 'usernameとpasswordを入力してください。'
            raise serializers.ValidationError(mag, code='authorization')
        
        # 認証が成功した場合、attrs 辞書に認証されたユーザーを追加します。
        attrs['user'] = user
        # attrs 辞書を戻り値として返します。これには、必要な認証情報や追加の検証後のデータが含まれます
        return attrs
    
# ユーザー情報取得のシリアライザ
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'nickname', 'email','coment') 
        
# ユーザー情報編集のシリアライザ
class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'nickname', 'email','coment')
    
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.email = validated_data.get('email', instance.email)
        instance.coment = validated_data.get('coment', instance.coment)
        instance.save()
        return instance