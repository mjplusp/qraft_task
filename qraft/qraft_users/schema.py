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

# 회원가입 API
class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    # 입력값 정의
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, password):
        user = get_user_model()(email=email)
        user.set_password(password) # 해쉬 함수를 이용해 암호화되어 저장
        user.save()

        logger.info(f'Create User Succeeded. User email: {email}') # 로그 작성

        return CreateUser(user=user)

# 로그인 API
class Login(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        
        # 들어온 요청으로부터 헤더 정보와 쿼리 내의 user 정보를 읽음
        user = info.context.user
        auth_header = info.context.headers.get('Authorization')

        # 헤더가 없을 경우 주어진 유저 로그인 정보를 이용해 인증 토큰 발행, return
        # 헤더가 있을 경우 Auth Header로부터 토큰 값을 읽어온 후 decode
        # 유저 데이터 중 겹치는 유저가 있을 경우 이미 로그인했다는 Exception 출력
        # 토큰 decode 결과가 제대로 나오지 않는다면 Valid하지 않다는 내용을 로깅하고, 마치 토큰이 없는 것처럼 새로운 토큰 발행
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