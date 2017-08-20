from mongoengine import Document, ListField, BooleanField, ReferenceField, StringField, PULL, NULLIFY, CASCADE
from flask_login import UserMixin


class User(Document, UserMixin):
    user_id = StringField(required=True, unique=True)
    password = StringField(required=True)


class Circle(Document):
    owner = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    name = StringField(required=True)
    members = ListField(ReferenceField(User, reverse_delete_rule=PULL), default=[])  # type: list[User]
    meta = {
        'indexes': [
            {'fields': ('owner', 'name'), 'unique': True}
        ]
    }

    def is_member(self, user):
        return filter(lambda member: member.id == user.id, self.members)


class Comment(Document):
    content = StringField(required=True)
    author = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)


class Post(Document):
    author = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    is_public = BooleanField(required=True)
    circle = ReferenceField(Circle, required=True, reverse_delete_rule=NULLIFY)
    content = StringField(required=True)
    comments = ListField(ReferenceField(Comment, reverse_delete_rule=PULL), default=[])
