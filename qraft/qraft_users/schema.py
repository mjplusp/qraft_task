from django.contrib.auth import get_user_model
import graphene
from graphene_django import DjangoObjectType
import graphql_jwt
from graphql_jwt.utils import jwt_decode
from jwt import DecodeError

import logging
logger = logging.getLogger("custom")

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()

class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    me = graphene.Field(UserType)

    def resolve_users(self, info, **kwargs):
        logger.info('Query user lists')
        return get_user_model().objects.all()
    
    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        return user

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        # username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, password):
        user = get_user_model()(email=email)
        user.set_password(password)
        user.save()

        logger.info(f'Create User Succeeded. User email: {email}')

        return CreateUser(user=user)

class Login(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):

        user = info.context.user
        auth_header = info.context.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            try:
                user_email = jwt_decode(token).get('email')
                logger.info(f'User already logged in with user email: {user_email}')
                raise Exception(f'이미 {user_email}로 로그인 하였습니다.(로그인 시도한 계정: {user.email})')
            except DecodeError:
                logger.info(f'Token exists but not valid. Logged in with user email: {user.email}. New Token Returned')
                return cls(user=user)
        else:
            logger.info(f'Logged in with user email: {user.email}. Token Returned')
            return cls(user=user)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    login = Login.Field()