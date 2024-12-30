from application.models import User, Post, UserBehavior
from django.utils import timezone

# 计算用户对标签的偏好值
def calculate_user_tag_preference(user):
    # 获取用户的所有浏览行为
    behaviors = UserBehavior.objects.filter(user=user, behavior_type=0)  # 假设0代表浏览
    user_tag_preference = {}
    for behavior in behaviors:
        post = behavior.target
        # 增加主标签的偏好值
        if post.main_tag_id not in user_tag_preference:
            user_tag_preference[post.main_tag_id] = 0
        user_tag_preference[post.main_tag_id] += 1
        # 增加副标签的偏好值
        for sub_tag in post.sub_tags.all():
            if sub_tag.id not in user_tag_preference:
                user_tag_preference[sub_tag.id] = 0
            user_tag_preference[sub_tag.id] += 5
    return user_tag_preference

# 生成推荐
def generate_recommendations(user_tag_preference):
    recommend_posts = []
    posts = Post.objects.all()
    for post in posts:
        # 计算用户对该帖子的兴趣程度
        score = 0
        if post.main_tag_id in user_tag_preference:
            score += user_tag_preference[post.main_tag_id]
        for sub_tag in post.sub_tags.all():
            if sub_tag.id in user_tag_preference:
                score += user_tag_preference[sub_tag.id] * 3
        # 计算时间分数
        now = timezone.now()
        time_difference = now - post.timestamp
        time_window = timezone.timedelta(days=3)
        if time_difference < time_window:  # 如果帖子在时间窗口内
            time_score = (time_window - time_difference).total_seconds()  # 计算时间分数
            time_score = time_score / (time_window.total_seconds() * 1.0) * 100
            # print(time_score)
            score += time_score  # 将时间分数转换为0-100的范围
        recommend_posts.append((post, score))
    recommend_posts.sort(key=lambda x: x[1], reverse=True)
    return [post[0] for post in recommend_posts]

# 主函数
def recommend_posts(user):
    user = User.objects.get(username=user)
    user_tag_preference = calculate_user_tag_preference(user)
    # print(user_tag_preference)
    return generate_recommendations(user_tag_preference)