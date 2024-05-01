from django.db import models


class BlogManager(models.Manager):
    def get_recently_added_blogs(self):
        return self.all()[:5]


class Blog(models.Model):
    title = models.CharField(max_length=255)
    cover_img = models.ImageField(upload_to='blogs/')
    content = models.TextField()
    objects = BlogManager()

    class Meta:
        db_table = 'blogs'
