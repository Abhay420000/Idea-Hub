from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from rest_framework import permissions
from api.permissions import IsOwnerOrReadOnly

from api.models import Articles, Comments, Ratings
from api.serializers import ArticleSerializer, ArticleCommentsSerializer, CommentSerializer

class PostAndComments(APIView, PageNumberPagination):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get(self, request, pid):
        article = Articles.objects.get(pid = pid)
        serializer = ArticleCommentsSerializer(instance=article)
        return Response(serializer.data)
    
    def put(self, request, pid, format=None):
        article = Articles.objects.get(pid = pid)
        
        data=request.data
        data['pid'] = article.pid
        
        if not data.get("title"):
            data['title'] = article.title
        if not data.get("body"):
            data['body'] = article.body
            
        serializer = ArticleSerializer(article, data = data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pid, format=None):
        article = Articles.objects.get(pid = pid)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EditComment(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get(self, request, pid, cid):
        comment = Comments.objects.get(cid = cid)
        serializer = CommentSerializer(instance=comment)
        return Response(serializer.data)
    
    def put(self, request, pid, cid):
        comment = Comments.objects.get(cid = cid)
        data=request.data
        data['cid'] = cid
        serializer = CommentSerializer(comment, data = data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pid, cid):
        comment = Comments.objects.get(cid = cid)
        comment.delete()
        return Response("Deleated!", status=status.HTTP_204_NO_CONTENT)

class Comment(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def post(self, request, pid):
        """Create a comment on a post"""
        article = Articles.objects.get(pid = pid)
        owner = request.user
        comment = request.data['comment']
        Comments(comment = comment, article = article, owner = owner).save()
        return Response("Created!", status=status.HTTP_201_CREATED)
         

class Year_Wise(APIView, PageNumberPagination):
    def get(self, request, year):
        #Filtering Objects of a particular year
        objs = Articles.objects.all().filter(created__year = year)
        
        #Pagination
        page = self.paginate_queryset(objs, request)
        if page is not None:
            serializer = ArticleSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleSerializer(objs, many=True)
        
        return Response(serializer.data)
    

class Year_Month_Wise(APIView, PageNumberPagination):
    def get(self, request, year, month):
        #Filtering Objects of a particular year and month
        objs = Articles.objects.all().filter(created__year = year).filter(created__month = month)
        
        #Pagination
        page = self.paginate_queryset(objs, request)
        if page is not None:
            serializer = ArticleSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleSerializer(objs, many=True)
        
        return Response(serializer.data)

class Year_Month_Day_Wise(APIView, PageNumberPagination):
    def get(self, request, year, month, day):
        #Filtering Objects of a particular year, month and day
        objs = Articles.objects.all().filter(created__year = year).filter(created__month = month).filter(created__day = day)
        
        #Pagination
        page = self.paginate_queryset(objs, request)
        if page is not None:
            serializer = ArticleSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleSerializer(objs, many=True)
        
        return Response(serializer.data)

class Posts(APIView, PageNumberPagination):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        """Show top 10 trending posts on a single page"""
        
        #Descending Order Sort
        objs = Articles.objects.all()#.order_by('-likes')
        
        #Pagination
        page = self.paginate_queryset(objs, request)
        if page is not None:
            serializer = ArticleSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleSerializer(objs, many=True)
        
        return Response(serializer.data)
    
    def post(self, request):
        """Upload a Post"""
        Articles(title = request.data['title'], body = request.data['body'], owner = request.user).save()
        return Response("Created!", status=status.HTTP_201_CREATED)
            

class Rate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pid):
        article = Articles.objects.get(pid = pid)
        
        op = request.data["op"]
        
        if not Ratings.objects.get(owner = request.user, article = article):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if op==1:
            Ratings(like = True, owner = request.user, article = article).save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif op==-1:
            Ratings(dislike = True, owner = request.user, article = article).save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pid):
        article = Articles.objects.get(pid = pid)
        rating = Ratings.objects.get(owner = request.user, article = article)
        
        op = request.data["op"]
        
        if op == 1:
            rating.dislike = False
            rating.like = True
            rating.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif op == -1:
            rating.dislike = True
            rating.like = False
            rating.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pid):
        article = Articles.objects.get(pid = pid)
        rating = Ratings.objects.get(owner = request.user, article = article)
        rating.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)