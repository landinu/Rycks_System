from flask_restful import Resource,reqparse
from flask_jwt import jwt_required,current_identity
from models.user import UserModel

class User(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument( 'field',
            type=str,
            required=True,
            help="A field is necessary."
    )
    parser.add_argument( 'value',
            type=str,
            required=True,
            help="A value must be specified."
    )

    @jwt_required()
    def get(self,name):
        user = UserModel.find_by_name(name)
        if user:
            return user.json()
        return {'message':'User not found'},404

    @jwt_required()
    def delete(self,name):
        user = UserModel.find_by_name(name)
        if user:
            user.delete_from_db()
            return {'message':'User {} was deleted'.format(user.username)}
        return {'message':'User not found'},404

    @jwt_required()
    def put(self,name):
        data = User.parser.parse_args()
        client = str(current_identity).replace('>','')
        client = client.split()
        print (type(client))
        print (client[1])
        client = UserModel.find_by_id(int(client[1]))
        user = UserModel.find_by_name(name)
        # Falta validar privilegios usuario
        if user and client.role_id == 1:
            #user = UserModel(name,**data)
            if data['field'] == 'password':
                user.password = data['value']
                user.save_to_db()
                return {'message':'User updated successfully'},201
            elif data['field'] == 'role':
                user.role_id = data['value']
                user.save_to_db()
                return {'message':'User updated successfully'},201
            else:
                return {'message':'Invalid field'},404
        elif user and client.role_id != 1:
                return {'message':'Operation Unauthorized'},404
        return {'message':'User not found'},404

class UserRegister(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument( 'username',
            type=str,
            required=True,
            help="This field cannot be blank."
    )

    parser.add_argument( 'password',
            type=str,
            required=True,
            help="This field cannot be blank."
    )

    def post(self):
        data = UserRegister.parser.parse_args()
        if UserModel.find_by_name(data['username']):
            return {"message":"User already exists."},400
        user = UserModel(**data)
        user.save_to_db()

        return {"message":"User created sucessfully."},201

class UserList(Resource):
    @jwt_required()
    def get(self):
        return {'users':[user.json() for user in UserModel.query.all()]}

