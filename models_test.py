import unittest
from mongoengine import connect, Document
from models import User, Circle


class MongomockTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MongomockTestCase, self).__init__(*args, **kwargs)
        self._mongo_objects = []  # type: list[Document]
        self._mongo_document_classes = []

    def __setattr__(self, key, value):
        super(MongomockTestCase, self).__setattr__(key, value)
        if isinstance(value, Document):
            self._mongo_objects.append(value)
            self._mongo_document_classes.append(value.__class__)

    @classmethod
    def setUpClass(cls):
        connect(cls.__name__, host='mongomock://localhost')

    def setUp(self):
        for mongo_object in self._mongo_objects:
            mongo_object.save()

    def tearDown(self):
        for document_class in self._mongo_document_classes:
            document_class.drop_collection()


class UserTests(MongomockTestCase):
    def __init__(self, *args, **kwargs):
        super(UserTests, self).__init__(*args, **kwargs)
        self._mongo_document_classes.append(User)

    def test_create(self):
        self.assertTrue(User.create('username', 'password'))
        self.assertEqual(len(User.objects()), 1)

    def test_create_duplicate_user_id(self):
        self.assertTrue(User.create('username', 'password'))
        self.assertFalse(User.create('username', 'password'))
        self.assertEqual(len(User.objects()), 1)

    def test_check(self):
        User.create('username', 'password')
        self.assertTrue(User.check('username', 'password'))

    def test_check_wrong_password(self):
        User.create('username', 'password')
        self.assertFalse(User.check('username', 'wrong password'))


class CircleTests(MongomockTestCase):
    def __init__(self, *args, **kwargs):
        super(CircleTests, self).__init__(*args, **kwargs)
        self._mongo_document_classes.append(User)
        self._mongo_document_classes.append(Circle)

    def setUp(self):
        super(CircleTests, self).setUp()
        User.create('username', 'password')
        self.current_user = User.objects.get(user_id='username')

    def test_create(self):
        self.assertTrue(Circle.create(self.current_user, 'circle'))
        self.assertEqual(len(Circle.objects(owner=self.current_user, name='circle')), 1)

    def test_create_duplicate_name(self):
        self.assertTrue(Circle.create(self.current_user, 'circle'))
        self.assertFalse(Circle.create(self.current_user, 'circle'))
        self.assertEqual(len(Circle.objects(owner=self.current_user, name='circle')), 1)
