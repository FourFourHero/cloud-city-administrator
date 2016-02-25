import logging
from badger.models import Badge

logger = logging.getLogger(__name__)

def create(user, badge_type):
    badge = Badge()
    badge.user = user
    badge.badge_type = badge_type
    badge.save()
    return badge

def count_by_user(user):
    count = Badge.objects.filter(user=user).count()
    logging.warn('count ' + str(count))
    return count

def delete_by_user_and_badge_type(user, badge_type):
    Badge.objects.filter(user=user, badge_type=badge_type).delete()