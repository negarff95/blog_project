from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from .serializers import PostSerializer, RateSerializer
from .models import Post
from core.pagination import CustomCursorPagination


class RateThrottle(UserRateThrottle):
    rate_limit = 5
    rate = f'{rate_limit}/day'


class PostView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request):
        """
        Get all posts and some details
        """
        queryset = Post.objects.all().order_by('-created_at')
        if request.query_params.get('post_id'):  # get specific post with id
            queryset = queryset.filter(id=request.query_params.get('post_id'))
        paginator = CustomCursorPagination()
        result_page_queryset = paginator.paginate_queryset(queryset, request)
        serializer = PostSerializer(
            result_page_queryset,
            many=True,
            context={
                'user': request.user,
            }
        )
        return paginator.get_paginated_response(serializer.data)


class RateView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )
    throttle_classes = (RateThrottle, )

    def post(self, request):
        """
        Submit post rate
        """
        serializer = RateSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


