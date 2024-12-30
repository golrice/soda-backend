import json
from django.http import JsonResponse
from .models import User, UserTag, Tag,Follow
from django.views.decorators.http import require_POST

def get_profile(request):
    username = request.GET.get('username')  # 获取 GET 请求中的用户名参数
    currentName = request.GET.get('currentName') # 获取是否是同一用户的标志
    existing_message = Follow.objects.filter(friend_id=username, user_id=currentName).first()
    if existing_message:
        followed = True
    else:
        followed = False
    if username == currentName:
        is_same_user = True
    else:
        is_same_user = False
    if username:
        try:
            # 查询用户信息
            user = User.objects.get(username=username)
            tags = UserTag.objects.filter(user_id=user.id)
            tag_names = [tag.name for tag in Tag.objects.filter(id__in=tags.values('tag_id'))]
            
            # 构建返回的数据
            profile_data = {
                'firstname': user.first_name,
                'lastname': user.last_name,                
                'intro': user.intros if user.intros else "这个人很懒，还没有简介。",
                'tags': tag_names,
                'email': user.email,
                'joined_date': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                'name': user.username,
                'fullname': user.first_name+" "+user.last_name,
                'followed': followed
            }
            
            # 如果是当前用户，返回额外的字段（如名字）
            if is_same_user:
                profile_data['firstname'] = user.first_name
                profile_data['lastname'] = user.last_name
            
            return JsonResponse(profile_data)

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    
    return JsonResponse({'error': 'Username parameter is missing'}, status=400)


@require_POST
def update_profile(request):
    data = json.loads(request.body.decode('utf-8'))
    username: str = data['username']
    intro: str = data['intro']
    email: str = data['email']
    firstname: str = data['firstname']
    lastname: str = data['lastname']
    if username:
        try:
            # 查询用户信息
            user = User.objects.get(username=username)
            
            # 更新用户信息
            user.intros = intro
            user.username = username
            user.email = email
            user.first_name = firstname
            user.last_name = lastname
            user.save()
            
            return JsonResponse({'message': 'Profile updated successfully'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    return JsonResponse({'error': 'Username, intro and tags parameters are missing'}, status=400)

def follow(request):
    data = json.loads(request.body.decode('utf-8'))
    currentUser:str = data['currentUser']
    targetUser:str = data['targetUser']
    followAction:bool = data['followAction']

    target_user = User.objects.filter(username=targetUser).first()
    current_user = User.objects.filter(username=currentUser).first()

    try:
        existing_message = Follow.objects.filter(friend=target_user, user=current_user).first()
        if not existing_message and not followAction:
            target_user = User.objects.filter(username=targetUser).first()
            current_user = User.objects.filter(username=currentUser).first()
            followship = Follow.objects.create(friend=target_user, user=current_user)
        elif existing_message and followAction:
            existing_message = Follow.objects.filter(friend=target_user, user=current_user).delete()
        return JsonResponse({'message': 'Profile updated successfully'}, status=200)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

def get_following(request):
    # 获取查询参数中的 username
    username = request.GET.get('username', None)

    # 如果没有传递 username 参数，返回错误
    if username is None:
        return JsonResponse({'error': 'No username provided'}, status=400)
    
    user = User.objects.filter(username=username).first()
    # 获取该用户关注的所有用户（即 user=username 的所有记录）
    friends = Follow.objects.filter(user=user).values_list('friend__username', flat=True)

    # 将查询结果转为列表并返回
    return JsonResponse({'friends': list(friends)}, status=200)


def get_followers(request):
    username = request.GET.get('username', None)
    
    if username is None:
        return JsonResponse({'error': 'No username provided'}, status=400)

    user = User.objects.filter(username=username).first()
    
    # 查询所有关注该用户的粉丝（friend=username）
    friends = Follow.objects.filter(friend=user).values_list('user__username', flat=True)

    # 将用户名列表转换成普通的列表并返回
    return JsonResponse({'friends': list(friends)}, status=200)