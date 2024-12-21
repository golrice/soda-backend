import json
import os
import time
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.core.cache import cache
from project.settings import MEDIA_ROOT

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
