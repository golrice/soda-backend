from django.db.models import Count
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.core.exceptions import ObjectDoesNotExist
from application.models import User, Post, UserBehavior

# 收集用户行为数据
def get_user_behavior_data(user):
    # 只获取传入用户的行为数据
    behaviors = UserBehavior.objects.filter(user=user).values_list('target', 'behavior_type')
    user_posts = {}
    for post_id, behavior_type in behaviors:
        if post_id not in user_posts:
            user_posts[post_id] = []
        user_posts[post_id].append(behavior_type)
    return user_posts

# 构建评分矩阵
def build_rating_matrix(user_posts):
    posts = Post.objects.all()
    post_ids = {post.id: post for post in posts}
    print(post_ids)
    
    # 创建一个空的评分矩阵，初始化为0
    matrix_size = len(posts)
    rating_matrix = np.zeros((matrix_size,))

    for post_id, behaviors in user_posts.items():
        post_obj = post_ids.get(post_id)
        if post_obj:
            print("555")
            post_index = list(post_ids.values()).index(post_obj)
            # 将行为类型转换为一个数值评分
            rating = np.mean(behaviors)  # 这里简单地取行为类型的平均值作为评分
            rating_matrix[post_index] = rating

    return rating_matrix

# 应用SVD
def apply_svd(rating_matrix, n_components=20):
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    # 由于我们只有用户对帖子的评分，而不是用户-帖子矩阵，我们需要转置评分矩阵
    rating_matrix = svd.fit_transform(rating_matrix.reshape(-1, 1))
    post_features = svd.components_.T
    return rating_matrix, post_features

# 生成推荐
def generate_recommendations(user_rating, post_features, num_recommendations=5):
    # 计算用户对所有帖子的预测评分
    predicted_ratings = user_rating.dot(post_features)
    # 获取评分最高的帖子ID
    recommended_post_indices = np.argsort(predicted_ratings)[-num_recommendations:][::-1]
    return [Post.objects.get(id=idx) for idx in recommended_post_indices]

# 主函数
def recommend_posts(user):
    print("111")
    user_posts = get_user_behavior_data(user)
    rating_matrix = build_rating_matrix(user_posts)
    print("222")
    user_rating, post_features = apply_svd(rating_matrix)
    return generate_recommendations(user_rating, post_features)