import json
from django.http import JsonResponse
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from application.models import User

# Create your views here.
def index(request):
    # return a json response
    return JsonResponse({'message': 'Hello, World!'})

def verify_password(request):
    if request.method == "POST":
        try:
            # 解析请求体
            data = json.loads(request.body)

            username = data.get("username")
            sha256_hash = data.get("sha256_hash")

            # 校验输入的数据
            if not username or not sha256_hash:
                return JsonResponse({"message": "Username and password hash are required."}, status=400)

            # 获取用户并验证
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({"message": "User does not exist."}, status=404)

            # 假设你存储的密码是已经加密的 SHA256 哈希
            stored_password_hash = user.password  # Django 默认将密码哈希存储在 password 字段中

            # 比较前端传来的密码哈希与存储的密码哈希是否相同
            if stored_password_hash == sha256_hash:
                return JsonResponse({"message": "Password is correct."}, status=200)
            else:
                return JsonResponse({"message": "Incorrect username or password."}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON."}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Invalid request method."}, status=405)

def if_username_exist(request):
    if request.method == "POST":
        try:
            # 解析请求体
            data = json.loads(request.body)
            username = data.get("username")

            # 检查是否提供了用户名
            if not username:
                return JsonResponse({"message": "Username is required."}, status=400)

            # 检查用户名是否存在
            if User.objects.filter(username=username).exists():
                return JsonResponse({"exists": True}, status=200)
            else:
                return JsonResponse({"exists": False}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON."}, status=400)
        except Exception as e:
            # 记录异常日志（如需要）
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Invalid request method."}, status=405)

def Register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            firstName = data.get("username")
            lastName = data.get("lastName")
            email = data.get("email")
            username = data.get("username")
            password = data.get("password")
            if not username or not firstName or not lastName or not email or not password:
                return JsonResponse({"message": "All the required field are needed."}, status=202)
            if User.objects.filter(username=username).exists():
                return JsonResponse({"exists": True}, status=201)
            user = User.objects.create(username=username, email=email, password=password,first_name=firstName,last_name=lastName)
            return JsonResponse({"message":"Register Succeeded."}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON."}, status=400)
        except IntegrityError as e:
        # 如果违反了数据库约束（例如，用户名已存在）
            print(f"Database IntegrityError: {str(e)}")
            return None
    
        except ValidationError as e:
        # 如果验证失败（例如，电子邮件格式错误）
            print(f"ValidationError: {str(e)}")
            return None
        except Exception as e:
            # 记录异常日志（如需要）
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Invalid request method."}, status=405)
