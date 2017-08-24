from mongoengine import Document, ListField, BooleanField, ReferenceField, StringField, PULL, CASCADE, NotUniqueError
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
        """
        Create a user
        :param (str) user_id: user id
        :param (str) password: password
        :return (bool): Whether creation is successful.
            If False, id is already taken
        """
        new_user = User()
        new_user.user_id = user_id
        new_user.password = generate_password_hash(password)
        try:
            new_user.save()
        except NotUniqueError:
            return False
        return True

    @staticmethod
    def check(user_id, password):
        """
        Check whether the user exists
        :param (str) user_id: user id
        :param (str) password: password
        :return (User|bool): Whether the user exists
        :exception (RuntimeError): If more than one user for the user id is found
        """
        users = User.objects(user_id=user_id)
        found_users = []
        for user in users:
            if check_password_hash(user.password, password):
                found_users.append(user)
        if not found_users:
            return False
        elif len(found_users) == 1:
            return found_users[0]
        else:
            raise RuntimeError('More than one user for user id {} found!'.format(user_id))

    def create_post(self, content, is_public, circles):
        """
        Create a post for the user
        :param (str) content: the content
        :param (bool) is_public: whether the post is public
        :param (list[Circle]) circles: circles to share with
        """
        new_post = Post()
        new_post.author = self.id
        new_post.content = content
        new_post.is_public = is_public
        new_post.circles = circles
        new_post.save()

    def create_comment(self, content, parent_post):
        """
        Create a comment for the user
        :param (str) content: the content
        :param (Post) parent_post: the post that this comment is attached to
        """
        new_comment = Comment()
        new_comment.author = self.id
        new_comment.content = content
        new_comment.save()
        parent_post.comments.append(new_comment)
        parent_post.save()


class Circle(Document):
    owner = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)  # type: User
    name = StringField(required=True)
    members = ListField(ReferenceField(User, reverse_delete_rule=PULL), default=[])  # type: list[User]
    meta = {
        'indexes': [
            {'fields': ('owner', 'name'), 'unique': True}
        ]
    }

    @staticmethod
    def create(owner, name):
        """
        Create a circle
        :param (User) owner: owner of the circle
        :param (str) name: name of the circle
        :return (bool): Whether creation is successful.
            If False, name is already taken
        """
        new_circle = Circle()
        new_circle.owner = owner.id
        new_circle.name = name
        try:
            new_circle.save()
        except NotUniqueError:
            return False
        return True

    def toggle_member(self, toggled_user):
        """
        Toggle a user's membership in the circle
        :param (User) toggled_user: toggled user
        """
        if self.check_member(toggled_user):
            self.members.remove(toggled_user)
        else:
            self.members.append(toggled_user)
        self.save()

    def check_member(self, user):
        """
        Check whether a user is in the circle
        :param (User) user: checked user
        :return (bool): whether the user is in the circle
        """
        return len(filter(lambda member: member.id == user.id, self.members)) != 0


class Comment(Document, CreatedAtMixin):
    author = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)  # type: User
    content = StringField(required=True)

    def owned_by(self, current_user, post):
        return self.author.id == current_user.id or post.owned_by(current_user)


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
                if circle.check_member(current_user):
                    return True
        return False

    def owned_by(self, current_user):
        return self.author.id == current_user.id

    @property
    def sharing_scope_str(self):
        if self.is_public:
            return '(public)'
        elif self.circles:
            return ', '.join(map(lambda circle: circle.name, self.circles))
        else:
            return '(private)'
