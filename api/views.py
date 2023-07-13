from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from rest_framework import permissions
from api.permissions import IsOwnerOrReadOnly

from api.models import Articles, Comments, Ratings
from django.db.models import Count
from api.serializers import ArticleSerializer, ArticleCommentsSerializer, CommentSerializer, RatingSerializer

from django.core.exceptions import ObjectDoesNotExist

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
        """
        Show top 10 trending posts on a single page.
        Articles need to have at least 1 like to be on trending page.
        """
        
        #Descending Order Sort
        objs = Articles.objects.filter(ratings__like = True).annotate(tlikes = Count('ratings')).order_by('-tlikes')
        
        #Pagination
        page = self.paginate_queryset(objs, request)
        if page is not None:
            serializer = ArticleSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ArticleSerializer(objs, many=True)
        
        return Response(serializer.data)
    
    def post(self, request):
        """Upload a Post"""
        article = Articles(title = request.data['title'], body = request.data['body'], owner = request.user)
        article.save()
        return Response(ArticleSerializer(article).data, status=status.HTTP_201_CREATED)
            

class Rate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pid):
        try:
            article = Articles.objects.get(pid = pid)
            user_rateings = Ratings.objects.get(article = article, owner = request.user)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
         
        serializer = RatingSerializer(user_rateings)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, pid):
        try:
            article = Articles.objects.get(pid = pid)
            action = request.data["action"]
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            #Already exists
            if Ratings.objects.get(owner = request.user, article = article):
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:  
            #if not exists          
            if action == 'like':
                rating = Ratings(like = True, owner = request.user, article = article)
                rating.save()
                return Response(RatingSerializer(rating).data, status=status.HTTP_201_CREATED)
            elif action == 'dislike':
                rating = Ratings(dislike = True, owner = request.user, article = article)
                rating.save()
                return Response(RatingSerializer(rating).data, status=status.HTTP_201_CREATED)
            
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, pid):
        try:
            article = Articles.objects.get(pid = pid)
            rating = Ratings.objects.get(owner = request.user, article = article)
            
            action = request.data["action"]
            
            if action == 'like':
                rating.dislike = False
                rating.like = True
                rating.save()
                return Response(RatingSerializer(rating).data, status=status.HTTP_200_OK)
            
            elif action == 'dislike':
                rating.dislike = True
                rating.like = False
                rating.save()
                return Response(RatingSerializer(rating).data, status=status.HTTP_200_OK)
        
        except ObjectDoesNotExist:    
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pid):
        try:
            article = Articles.objects.get(pid = pid)
            rating = Ratings.objects.get(owner = request.user, article = article)
        except ObjectDoesNotExist:
            Response(status=status.HTTP_404_NOT_FOUND)
            
        rating.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)