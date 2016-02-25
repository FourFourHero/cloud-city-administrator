import logging

from django.db import models
from django.contrib.auth.models import User
from badger.models.basemodel import BaseModel

class BadgeManager(models.Manager):
    pass

class Badge(BaseModel):
    user = models.ForeignKey(User)
    badge_type = models.IntegerField(default=-1)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    objects = BadgeManager()

    class Meta:
        db_table = 'badger_badge'
        app_label = 'badger'

    def __unicode__(self):
        return self.user.username + ':' + str(self.id)

    def __json__(self):
        json = {}
        json['id'] = self.id
        json['user'] = self.user.username
        json['badge_type'] = self.badge_type
        return json