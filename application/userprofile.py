import json
from django.http import JsonResponse
from .models import User, UserTag, Tag
from django.views.decorators.http import require_POST

def get_profile(request):
    username = request.GET.get('username')  # 获取 GET 请求中的用户名参数
    if username:
        try:
            # 查询用户信息及标签
            user = User.objects.get(username=username)
            tags = UserTag.objects.filter(user_id=user.id)
            tag_names = [tag.name for tag in Tag.objects.filter(id__in=tags.values('tag_id'))]
            
            # 处理 intro 字段
            intro = user.intros if user.intros else "This guy is lazy. He/She hasn't have an introduce yet."
            
            return JsonResponse({
                'name': user.username,
                'avatar': user.icon,  # 假设头像路径存在 `icon` 列
                'intro': intro,
                'tags': tag_names,
            })
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    return JsonResponse({'error': 'Username parameter is missing'}, status=400)

@require_POST
def update_profile(request):
    data = json.loads(request.body.decode('utf-8'))
    username: str = data['username']
    intro: str = data['intro']

    if username and intro:
        try:
            # 查询用户信息
            user = User.objects.get(username=username)
            
            # 更新用户信息
            user.intros = intro
            user.save()
            
            return JsonResponse({'message': 'Profile updated successfully'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    return JsonResponse({'error': 'Username, intro and tags parameters are missing'}, status=400)
