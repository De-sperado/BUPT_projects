import datetime

from django.db import models

# Create your models here.
from django.utils import timezone


class DOC(models.Model):
    doc_title=models.CharField(max_length=200)
    doc_time=models.DateTimeField('DOC PUBLISHED')
    doc_text=models.CharField(max_length=400)
    def __str__(self):
        return self.doc_text
    def was_published_recently(self):
        return self.doc_time>=timezone.now()-datetime.timedelta(days=1)