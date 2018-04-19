from django.db import models
from django.conf import settings

class LabelType(models.Model):
    # Definition of labels (not the actual labels that will annotate a given video)
    # that will be used in the annotation system
    # e.g., "baby_crying", etc.
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Video(models.Model):
    # A `Video` is characterized by its original `url` (youtube url, for instance)
    # it does not have to be a remote URL though, `url` could start directly
    # by /, in this case it will redirect to the folder /static/videos
    # of the project.
    url = models.CharField(max_length=255, unique=True)
    query_label_type = models.ForeignKey(LabelType, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.url

class Label(models.Model):
    # The annotation of a given `video` by a `user`
    label_type = models.ForeignKey(LabelType, on_delete=models.CASCADE)
    video_has_label = models.BooleanField()
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now=True)
