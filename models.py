from mongoengine import Document, ListField, BooleanField, ReferenceField, StringField, PULL, CASCADE
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class CreatedAtMixin(object):
    @property
    def created_at(self):
        return self.id.generation_time


class User(Document, UserMixin):
    user_id = StringField(required=True, unique=True)
    password = StringField(required=True)

    @staticmethod
    def create(user_id, password):
        new_user = User()
        new_user.user_id = user_id
        new_user.password = generate_password_hash(password)
        new_user.save()

    @staticmethod
    def check(user_id, password):
        users = User.objects(user_id=user_id)
        found_users = []
        for user in users:
            if check_password_hash(user.password, password):
                found_users.append(user)
        return found_users


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
    author = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)  # type: User
    content = StringField(required=True)

    def can_remove(self, current_user, post):
        return self.author.id == current_user.id or post.can_remove(current_user)


class Post(Document, CreatedAtMixin):
    author = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)  # type: User
    content = StringField(required=True)
    is_public = BooleanField(required=True)
    circles = ListField(ReferenceField(Circle, reverse_delete_rule=PULL), default=[])  # type: list[Circle]
    comments = ListField(ReferenceField(Comment, reverse_delete_rule=PULL), default=[])  # type: list[Comment]

    def shared_with(self, current_user):
        if self.author.id == current_user.id:
            return True
        elif self.is_public:
            return True
        else:
            for circle in self.circles:
                if circle.is_member(current_user):
                    return True
        return False

    def can_remove(self, current_user):
        return self.author.id == current_user.id

    @property
    def sharing_scope_str(self):
        if self.is_public:
            return '(public)'
        elif self.circles:
            return ', '.join(map(lambda circle: circle.name, self.circles))
        else:
            return '(private)'
