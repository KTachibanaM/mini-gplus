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

    # User

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

    # Post

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

    def owns_post(self, post):
        """
        Whether the user owns a post
        :param (Post) post: the post
        :return (bool): whether the user owns the post
        """
        return self.id == post.author.id

    def sees_post(self, post):
        """
        Whether the user can see a post
        :param (Post) post: the post
        :return (bool): whether the user sees the post
        """
        if self.owns_post(post):
            return True
        elif post.is_public:
            return True
        else:
            for circle in post.circles:
                if circle.check_member(self):
                    return True
        return False

    def delete_post(self, post):
        """
        Delete a post
        :param (Post) post: the post
        :return (bool): whether it's authorized
        """
        if post.author.id == self.id:
            post.delete()
            return True
        else:
            return False

    def sees_posts(self, by_user=None):
        """
        All posts that are visible to the user
        :param (User) by_user: posts that are authored by this user
        :return (list[Post]): all posts that are visible to the user, reverse chronologically ordered
        """
        if by_user is None:
            posts = Post.objects()
        else:
            posts = Post.objects(author=by_user)
        posts = filter(lambda post: self.sees_post(post), posts)
        return list(reversed(sorted(posts, key=lambda post: post.created_at)))

    # Comment

    def create_comment(self, content, parent_post):
        """
        Create a comment for the user
        :param (str) content: the content
        :param (Post) parent_post: the post that this comment is attached to
        :return (bool): whether it's authorized
        """
        if self.sees_post(parent_post):
            new_comment = Comment()
            new_comment.author = self.id
            new_comment.content = content
            new_comment.save()
            parent_post.comments.append(new_comment)
            parent_post.save()
            return True
        else:
            return False

    def owns_comment(self, comment, parent_post):
        """
        Whether the user owns a comment
        :param (Comment) comment: the comment
        :param (Post) parent_post: its parent post
        :return (bool): whether hte user owns a comment
        """
        return self.owns_post(parent_post) or self.id == comment.author.id

    def delete_comment(self, comment, parent_post):
        """
        Delete a comment
        :param (Comment) comment: the comment
        :param (Post) parent_post: comment's parent post
        :return: whether it's authorized
        """
        if self.owns_comment(comment, parent_post):
            parent_post.comments.remove(comment)
            comment.delete()
            return True
        else:
            return False

    # Circle

    def create_circle(self, name):
        """
        Create a circle
        :param (str) name: name of the circle
        :return (bool): Whether creation is successful.
            If False, name is already taken
        """
        new_circle = Circle()
        new_circle.owner = self.id
        new_circle.name = name
        try:
            new_circle.save()
        except NotUniqueError:
            return False
        return True

    def toggle_member(self, circle, toggled_user):
        """
        Toggle a user's membership in a circle
        :param (Circle) circle: the circle
        :param (User) toggled_user: toggled user
        :returns (bool): whether it's authorized
        """
        if circle.owner.id == self.id:
            if circle.check_member(toggled_user):
                circle.members.remove(toggled_user)
            else:
                circle.members.append(toggled_user)
            circle.save()
            return True
        else:
            return False

    def delete_circle(self, circle):
        """
        Delete a circle
        :param (Circle) circle: the circle
        :return (bool): whether it's authorized
        """
        if circle.owner.id == self.id:
            circle.delete()
            return True
        else:
            return False


class Circle(Document):
    owner = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)  # type: User
    name = StringField(required=True)
    members = ListField(ReferenceField(User, reverse_delete_rule=PULL), default=[])  # type: list[User]
    meta = {
        'indexes': [
            {'fields': ('owner', 'name'), 'unique': True}
        ]
    }

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
