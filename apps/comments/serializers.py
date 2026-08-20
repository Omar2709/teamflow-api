from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    task = serializers.IntegerField(
        source="task_id",
        read_only=True,
    )

    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "task",
            "author",
            "content",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "task",
            "author",
            "created_at",
            "updated_at",
        )

    def get_author(self, comment):
        if comment.author is None:
            return None

        return {
            "id": comment.author.pk,
            "username": comment.author.username,
            "email": comment.author.email,
        }

    def validate_content(self, value):
        normalized_content = value.strip()

        if not normalized_content:
            raise serializers.ValidationError(
                "El comentario no puede estar vacío."
            )

        return normalized_content