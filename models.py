from mongoengine import Document, ListField, BooleanField, ReferenceField, StringField, PULL, NULLIFY, CASCADE
from flask_login import UserMixin


class Circle(Document):
    owner = ReferenceField('User', required=True)
    name = StringField(required=True)
    members = ListField(ReferenceField('User'), default=[])


class User(Document, UserMixin):
    user_id = StringField(required=True, unique=True)
    password = StringField(required=True)
    posts = ListField(ReferenceField('Post'), default=[])  # type: list[Post]


class Post(Document):
    is_public = BooleanField(required=True)
    circle = ReferenceField('Circle', required=True)
    content = StringField(required=True)
    comments = ListField(ReferenceField('Comment'), default=[])


class Comment(Document):
    content = StringField(required=True)
    user = ReferenceField('User', required=True)


Circle.register_delete_rule(Circle, 'owner', CASCADE)
Circle.register_delete_rule(Circle, 'members', PULL)
User.register_delete_rule(User, 'posts', PULL)
Post.register_delete_rule(Post, 'circle', NULLIFY)
Post.register_delete_rule(Post, 'comments', PULL)
Comment.register_delete_rule(Comment, 'user', CASCADE)
