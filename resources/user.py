from flask_restful import reqparse, Resource
from models import User as DbUser
from flask_jwt_extended import jwt_required, get_jwt_identity

user_parser = reqparse.RequestParser()
user_parser.add_argument('id', type=str, required=True)
user_parser.add_argument('password', type=str, required=True)


class UserList(Resource):
    def post(self):
        args = user_parser.parse_args()
        successful = DbUser.create(args['id'], args['password'])
        if successful:
            return {'id': args['id']}, 201
        else:
            return {'message': {'id': 'id is already taken'}}, 409

    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        other_users = [
            {'id': user.user_id, 'createdAtSeconds': user.created_at_unix_seconds}
            for user in DbUser.objects(user_id__ne=user_id)
        ]
        return other_users, 200


class Me(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        return {'id': user_id}, 200
