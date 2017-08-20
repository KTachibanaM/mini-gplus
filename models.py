from mongoengine import Document, ListField, BooleanField, ReferenceField, StringField, PULL, NULLIFY, CASCADE


class Circle(Document):
    name = StringField(required=True)
    members = ListField(ReferenceField('User'), default=[])


class User(Document):
    user_id = StringField(required=True, unique=True)
    password = StringField(required=True)
    circles = ListField(ReferenceField('Circle'), default=[])
    posts = ListField(ReferenceField('Post'), default=[])


class Post(Document):
    is_public = BooleanField(required=True)
    circle = ReferenceField('Circle', required=True)
    content = StringField(required=True)
    comments = ListField(ReferenceField('Comment'), default=[])


class Comment(Document):
    content = StringField(required=True)
    user = ReferenceField('User', required=True)


Circle.register_delete_rule(Circle, 'members', PULL)
Circle.register_delete_rule(User, 'circles', PULL)
Circle.register_delete_rule(User, 'posts', PULL)
Circle.register_delete_rule(Post, 'circle', NULLIFY)
Circle.register_delete_rule(Post, 'comments', PULL)
Circle.register_delete_rule(Comment, 'user', CASCADE)
