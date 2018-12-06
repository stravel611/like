# coding: utf-8
import unittest
from like import create_app
from like.exts import db
from like.models import Permission, Role, User


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('test')
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

        db.create_all()
        Permission.init_permission()
        Role.init_role()

    def tearDown(self):
        db.drop_all()
        self.context.pop()

    def test_database(self):
        perm = Permission.query.get(1)
        roles = Role.query.all()
        self.assertEqual('PUBLISH', perm.name)
        self.assertEqual(3, len(roles))
        self.assertIn(perm, roles[1].permissions)
