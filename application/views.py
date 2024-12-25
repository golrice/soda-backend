import json
import os
import time
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.core.cache import cache
from project.settings import MEDIA_ROOT
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError

# Create your views here.
def index(request):
    # return a json response
    return JsonResponse({'message': 'Hello, World!'})

@require_POST
def create_post(request):
    data = json.loads(request.body.decode('utf-8'))
    title: str = data['title']
    content: str =  data['content']

    if title == '' or content == '':
        return JsonResponse({'message': 'Title and content are required!'}, status=400)

    # check if the post already exists
    dir_path = os.path.join(MEDIA_ROOT, 'posts')
    if os.path.exists(os.path.join(dir_path, title + '.txt')):
        return JsonResponse({'message': 'Post already exists!'}, status=400)
    
    # create the post file
    file_path = os.path.join(dir_path, title + '.txt')
    with open(file_path, 'w') as f:
        f.write(content)

    return JsonResponse({'message': 'Post created successfully!'}, status=200)

def get_posts(request):
    posts = cache.get('posts')
    if posts is not None:
        return JsonResponse({'posts': posts})

    dir_path = os.path.join(MEDIA_ROOT, 'posts')
    
    if not os.path.exists(dir_path):
        return JsonResponse({'error': 'Directory not found'}, status=404)

    try:
        posts = [
            {
                'name': os.path.splitext(file)[0],
                'creationTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(os.path.join(dir_path, file)))),
                'author': 'golrice'
            }
            for file in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, file))  # 确保是文件
        ]

        # 按创建时间排序
        posts.sort(key=lambda x: x['creationTime'], reverse=True)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    cache.set('posts', posts, 60)  # 缓存 60 秒
    return JsonResponse({'posts': posts})


def get_post(request, post_name):
    cache_data = cache.get(post_name)
    if cache_data is not None:
        return JsonResponse({'title': cache_data[0], 'content': cache_data[1]})

    # read the file 'post_name.txt'
    file_path = os.path.join(MEDIA_ROOT, 'posts', post_name + '.txt')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()

        cache.set(post_name, (post_name, content), 60)  # 缓存 60 秒
        return JsonResponse({'title': post_name, 'content': content})
    else:
        return HttpResponse(status=404)

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
        except Exception as e:
            # 记录异常日志（如需要）
            return JsonResponse({"message": str(e)}, status=500)
        except IntegrityError as e:
        # 如果违反了数据库约束（例如，用户名已存在）
            print(f"Database IntegrityError: {str(e)}")
            return None
    
        except ValidationError as e:
        # 如果验证失败（例如，电子邮件格式错误）
            print(f"ValidationError: {str(e)}")
            return None
    else:
        return JsonResponse({"message": "Invalid request method."}, status=405)
