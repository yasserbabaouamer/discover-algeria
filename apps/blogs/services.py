from .models import Blog


def get_some_blogs():
    return Blog.objects.get_recently_added_blogs()
