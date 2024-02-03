from django.db import models


class QandAModel(models.Model):
    question = models.TextField(blank=True, null=True)
    options = models.TextField(blank=True, null=True)
    section = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    answer = models.CharField(max_length=255, null=True, blank=True)
    solution = models.TextField(blank=True, null=True)
    examtype = models.CharField(max_length=255, null=True, blank=True)
    examyear = models.CharField(max_length=255, null=True, blank=True)
    source_id = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question[:100]

    class Meta:
        db_table = 'qanda'
        app_label = 'qanda'
