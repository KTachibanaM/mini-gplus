from mongoengine import Document, ListField, BooleanField, ReferenceField, StringField, PULL, CASCADE
from flask_login import UserMixin


class CreatedAtMixin(object):
    @property
    def created_at(self):
        return self.id.generation_time


class User(Document, UserMixin):
    user_id = StringField(required=True, unique=True)
    password = StringField(required=True)


class Circle(Document):
    owner = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)  # type: User
    name = StringField(required=True)
    members = ListField(ReferenceField(User, reverse_delete_rule=PULL), default=[])  # type: list[User]
    meta = {
        'indexes': [
            {'fields': ('owner', 'name'), 'unique': True}
        ]
    }

    def is_member(self, user):
        return filter(lambda member: member.id == user.id, self.members)


class Comment(Document, CreatedAtMixin):
    content = StringField(required=True)
    author = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)  # type: User


class Post(Document, CreatedAtMixin):
    author = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)  # type: User
    content = StringField(required=True)
    is_public = BooleanField(required=True)
    circles = ListField(ReferenceField(Circle, reverse_delete_rule=PULL), default=[])  # type: list[Circle]
    comments = ListField(ReferenceField(Comment, reverse_delete_rule=PULL), default=[])  # type: list[Comment]

    @property
    def sharing_scope_str(self):
        if self.is_public:
            return '(public)'
        elif self.circles:
            return ', '.join(map(lambda circle: circle.name, self.circles))
        else:
            return '(private)'
