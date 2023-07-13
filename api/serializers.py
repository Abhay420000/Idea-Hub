from rest_framework import serializers
from . models import Articles, Comments, Ratings

class ArticleSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Articles
        fields = '__all__'

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
      
class CommentSerializer(DynamicFieldsModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    article = serializers.ReadOnlyField(source='article.pid')
    class Meta:
        model = Comments
        fields = '__all__'

class ArticleCommentsSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True, fields=('cid', 'owner', 'comment', 'created'))
    owner = serializers.ReadOnlyField(source='owner.username')
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    
    class Meta:
        model = Articles
        fields = ['pid', 'title', 'body', 'owner', 'likes', 'dislikes', 'updated', 'created', 'comments']
    
    def get_likes(self, obj):
        #print(obj)
        return Ratings.objects.filter(like = True).filter(article = obj).count()
    
    def get_dislikes(self, obj):
        return Ratings.objects.filter(dislike = True).filter(article = obj).count()

class RatingSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Ratings
        fields = "__all__"