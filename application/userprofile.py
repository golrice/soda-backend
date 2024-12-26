from django.http import JsonResponse
from .models import User, UserTag, Tag

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
