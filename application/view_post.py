import json
import os
import time
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from project.settings import MEDIA_ROOT, POSTS_DIR
from application.models import Post, User
from application.models import PostTag

@require_POST
def create_post(request):
    data = json.loads(request.body.decode('utf-8'))
    title: str = data['title']
    content: str =  data['content']
    username: str = data['username']

    if title == '' or content == '':
        return JsonResponse({'message': 'Title and content are required!'}, status=400)

    # check if the post already exists
    if os.path.exists(os.path.join(POSTS_DIR, title)):
        # 直接修改原文件的内容
        try:
            with open(os.path.join(POSTS_DIR, title), 'w') as f:
                f.write(content)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
        return JsonResponse({'message': 'Post updated successfully!'}, status=200)
    
    # create the post file
    file_path = os.path.join(POSTS_DIR, title)
    try:
        with open(file_path, 'w') as f:
            f.write(content)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)

    try:
        user = User.objects.get(username=username)
        post = Post(title=title, url=os.path.join(POSTS_DIR, title), author=user)
        post.save()
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)

    return JsonResponse({'message': 'Post created successfully!'}, status=200)

def get_posts(request):
    if not os.path.exists(POSTS_DIR):
        return JsonResponse({'error': 'Directory not found'}, status=404)

    try:
        # posts = [
        #     {
        #         'name': file,
        #         'creationTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(os.path.join(POSTS_DIR, file)))),
        #         'author': 'golrice'
        #     }
        #     for file in os.listdir(POSTS_DIR)
        #     if os.path.isfile(os.path.join(POSTS_DIR, file))  # 确保是文件
        # ]
        posts = []
        for post in Post.objects.all():
            with open(post.url, 'r') as f:
                posts.append({
                    'title': post.title,
                    'author': post.author.username,
                    'creationTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(post.url))),
                })

        # 按创建时间排序
        posts.sort(key=lambda x: x['creationTime'], reverse=True)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'posts': posts})

def get_posts_by_username(request, username):
    try:
        user = User.objects.get(username=username)
        posts = [
            {
                'title': post.title,
                'author': username,
                'creationTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(post.url))),
            }
            for post in Post.objects.filter(author=user)
        ]
        return JsonResponse({'posts': posts})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_post(request, post_name):
    # read the file 'post_name'
    post = Post.objects.filter(title=post_name).first()
    if os.path.exists(post.url):
        with open(post.url, 'r') as f:
            content = f.read()

        return JsonResponse({'title': post_name, 'content': content, 'author': post.author.username})
    else:
        return HttpResponse(status=404)

def delete_post(request, post_name):
    file_path = os.path.join(MEDIA_ROOT, 'posts', post_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        return JsonResponse({'message': 'Post deleted successfully!'}, status=200)
    else:
        return JsonResponse({'error': 'Post not found!'}, status=404)

def pal_query(request):
    query = request.GET.get('query', '')
    if query == '':
        return JsonResponse({'data': []})

    # 查询数据库User表中username包含query的用户
    users = User.objects.filter(username__icontains=query)
    # 将users转化为json格式
    users_json = [user.username for user in users]
    print(users_json)

    return JsonResponse({'data': users_json})
