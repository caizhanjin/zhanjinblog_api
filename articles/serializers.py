from rest_framework import serializers

from .models import Articles, Collections, Labels, Messages, Recent


class ArticlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = "__all__"


class CollectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collections
        fields = "__all__"


class LabelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labels
        fields = "__all__"


class MessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = "__all__"


class RecentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recent
        fields = "__all__"
