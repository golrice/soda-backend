import json
import os
import time
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from project.settings import MEDIA_ROOT, POSTS_DIR
from application.models import Post, User
from application.models import Tag
from application.post_tag import get_tags
from django.db.models import F
from application.push_post import recommend_posts
import re

def is_valid_filename(filename):
    # 定义非法字符的正则表达式
    illegal_chars = r'[<>:"/\\|?*]'
    # 检查是否包含非法字符
    if re.search(illegal_chars, filename):
        return False
    # 检查是否以空格开头或结尾
    if filename.startswith(' ') or filename.endswith(' '):
        return False
    # 检查是否为Windows保留名称（不区分大小写）这是AI给我的保留名称，不知道有没有其他的，也不知道linux的会不会不一样
    windows_reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    if filename.upper() in windows_reserved_names:
        return False
    # 检查文件名长度（例如，最大255个字符）
    if len(filename) > 100:
        return False
    # 如果所有检查都通过，则文件名合法
    return True

def save_tags_to_post(post, answer):
    main_tag_name = answer.get('main', '')
    sub_tag_names = [answer.get(f'label{i+1}', '') for i in range(5)]

    # 去重并移除主标签
    sub_tag_names = list(set(sub_tag_names))
    if main_tag_name in sub_tag_names:
        sub_tag_names.remove(main_tag_name)
    sub_tag_names = [name for name in sub_tag_names if name]  # 过滤空字符串
    sub_tag_names = sub_tag_names[:5]  # 保证不超过五个
    # print(main_tag_name, sub_tag_names)
    # 获取或创建标签
    if main_tag_name:
        main_tag, _ = Tag.objects.get_or_create(tag_name=main_tag_name)
    else:
        main_tag = None

    sub_tags = []
    for name in sub_tag_names:
        if name:
            tag, _ = Tag.objects.get_or_create(tag_name=name)
            sub_tags.append(tag)

    # 设置标签并保存
    post.main_tag = main_tag
    post.sub_tags.set(sub_tags)
    post.save()

@require_POST
def create_post(request):    
    # 解析请求体中的JSON数据
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    title: str = data['title']
    content: str =  data['content']
    username: str = data['username']
    prv_title: str = data['prv_title']

    if title == '' or content == '':
        return JsonResponse({'message': 'Title and content are required!'}, status=400)

    # 检查标题是否是合法的文件名
    if not is_valid_filename(title):
        return JsonResponse({'error': 'Invalid title, it cannot be used as a valid filename'}, status=400)

    # check if the post already exists
    if os.path.exists(os.path.join(POSTS_DIR, title)) and not prv_title:
        # 直接修改原文件的内容
        try:
            with open(os.path.join(POSTS_DIR, title), 'w') as f:
                f.write(content)
            post = Post.objects.get(url=os.path.join(POSTS_DIR, title))
            answer = get_tags(content)
            save_tags_to_post(post, answer)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
        return JsonResponse({'message': 'Post updated successfully!'}, status=200)

    if prv_title and os.path.exists(os.path.join(POSTS_DIR, prv_title)):
        user = User.objects.get(username=username)
        post = Post.objects.get(title=prv_title)
        if post.author != user:
            return JsonResponse({'message': 'You are not the author of this post!'}, status=403)
        
        os.remove(os.path.join(POSTS_DIR, prv_title))
        post.delete()
    
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
    answer = get_tags(content)
    save_tags_to_post(post, answer)

    return JsonResponse({'message': 'Post created successfully!'}, status=200)

def get_posts(request):
    if not os.path.exists(POSTS_DIR):
        return JsonResponse({'error': 'Directory not found'}, status=404)

    try:
        posts = []
        # for post in Post.objects.all():
        #     if not os.path.exists(post.url):
        #         continue
        #     with open(post.url, 'r') as f:
        #         posts.append({
        #             'title': post.title,
        #             'author': post.author.username,
        #             'creationTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(post.url))),
        #         })

        # # 按创建时间排序
        # posts.sort(key=lambda x: x['creationTime'], reverse=True)
        # print(posts)

        # 获取Authorization头部中的username
        token = request.headers.get('Authorization')

        flag = False
        # 使用Bearer Token，则进一步提取token字符串（但咱这里是username）
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]
            flag = True
        
        if flag:
            user = User.objects.get(username=token)
            new_posts = recommend_posts(user)
            # print(new_posts)
    
        for post in new_posts:
            if not os.path.exists(post.url):
                continue
            # print(post.title)
            with open(post.url, 'r') as f:
                posts.append({
                    'title': post.title,
                    'author': post.author.username,
                    'creationTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(post.url))),
                })

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

from application.models import UserBehavior
from django.utils import timezone
def get_post(request, post_name):
    # 获取Authorization头部中的username
    token = request.headers.get('Authorization')

    flag = False
    # 使用Bearer Token，则进一步提取token字符串（但咱这里是username）
    if token and token.startswith('Bearer '):
        token = token.split(' ')[1]
        flag = True
    # else:
    #     return JsonResponse({'error': '请登录以享受完整体验！'}, status=401)
    # read the file 'post_name'
    post = Post.objects.filter(title=post_name).first()
    if os.path.exists(post.url):
        with open(post.url, 'r') as f:
            content = f.read()

        if flag and str(post.author) != token:
            _user = User.objects.get(username=token)
            # 记录用户行为信息
            UserBehavior.objects.create(
                user=_user,
                behavior_type=0,  # 假设0代表浏览行为
                target=post,
                timestamp=timezone.now(),
            )
        
        if flag and str(post.author) != token:
            # 如果不是作者，增加浏览次数
            post.view_count = F('view_count') + 1
            post.save()

        return JsonResponse({'title': post_name, 'content': content, 'author': post.author.username})
    else:
        return HttpResponse(status=404)

def delete_post(request, post_name):
    file_path = os.path.join(MEDIA_ROOT, 'posts', post_name)
    author = request.GET.get('author', '')
    if author == '':
        return JsonResponse({'error': 'Author not found!'}, status=400)
    # 判断当前用户是否是作者
    try:
        user = User.objects.get(username=author)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Author not found!'}, status=400)

    try:
        post = Post.objects.get(title=post_name)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found!'}, status=404)

    if user != post.author:
        return JsonResponse({'error': 'You are not the author of this post!'}, status=403)

    if os.path.exists(file_path):
        post.delete()
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

    return JsonResponse({'data': users_json})
