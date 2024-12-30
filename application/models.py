from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    last_login = models.DateTimeField(null=True)
    first_name = models.CharField(max_length=255,null=True)
    last_name = models.CharField(max_length=255,null=True)
    email = models.CharField(max_length=255,null=True)
    date_joined = models.DateField(null=True)
    icon = models.ImageField(upload_to='avatars/',null=True)
    intros = models.TextField(null=True)
    def __str__(self):
        return self.username

class Tag(models.Model):
    tag_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.tag_name

class Picture(models.Model):
    url = models.URLField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pictures')

    def __str__(self):
        return self.url

class Post(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    main_tag = models.ForeignKey(Tag, related_name='main_posts', on_delete=models.SET_NULL, null=True, blank=True)
    sub_tags = models.ManyToManyField(Tag, related_name='sub_posts', blank=True)
    view_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)

    def clean(self):
        if self.main_tag and self.main_tag in self.sub_tags.all():
            raise ValidationError("主标签不能是小标签之一。")
        if self.sub_tags.count() > 5:
            raise ValidationError("最多只能选择五个小标签。")

    def __str__(self):
        return self.title or "Untitled"

class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

class Like(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('author', 'post')

    def __str__(self):
        return f"Like by {self.author.username} on {self.post.title}"

class UserTag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'tag')

    def __str__(self):
        return f"{self.user.username} tagged with {self.tag.tag_name}"

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers',to_field="username")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends',to_field="username")

    class Meta:
        unique_together = ('user', 'friend')

    def __str__(self):
        return f"{self.user.username} is friends with {self.friend.username}"


class UserBehavior(models.Model):
    # 用户外键，关联到User模型
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behaviors')
    # 行为类型（如：浏览、点赞、评论等）用一个数字表示，比如0代表浏览，1代表点赞，2代表评论
    behavior_type = models.IntegerField()
    # 行为对象，可能是帖子、图片等，这里使用外键关联到Post模型
    target = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='behaviors')
    # 行为发生的时间
    timestamp = models.DateTimeField(default=timezone.now)
    # 行为的额外数据，比如浏览时间、点赞的权重等，目前用不上
    # extra_data = models.JSONField(null=True, blank=True)

    class Meta:
        # 确保每个用户对于同一目标的行为是唯一的
        unique_together = ('user', 'target', 'behavior_type', 'timestamp')

    def __str__(self):
        return f"{self.user.username} {self.behavior_type} on {self.target.title} at {self.timestamp}"