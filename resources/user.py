from flask_restful import reqparse, Resource
from models import User as DbUser

user_parser = reqparse.RequestParser()
user_parser.add_argument('id', type=str, required=True)
user_parser.add_argument('password', type=str, required=True)


class UserList(Resource):
    def post(self):
        args = user_parser.parse_args()
        id_not_taken = DbUser.create(args['id'], args['password'])
        if id_not_taken:
            return {'id': args['id']}, 201
        else:
            return {'message': {'id': 'id is already taken'}}, 409
