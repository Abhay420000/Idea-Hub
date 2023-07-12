from rest_framework import serializers
from . models import Articles, Comments, Ratings

class ArticleSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Articles
        fields = '__all__'
        
class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    article = serializers.ReadOnlyField(source='article.pid')
    class Meta:
        model = Comments
        fields = '__all__'

class ArticleCommentsSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    
    class Meta:
        model = Articles
        fields = ['pid', 'title', 'body', 'owner', 'updated', 'created', 'comments']
    
    def get_likes(self):
        return Ratings.objects.filter(like = True).count()
    
    def get_dislikes(self):
        return Ratings.objects.filter(dislike = False).count()