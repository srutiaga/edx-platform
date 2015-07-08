import logging
import json
import requests
from django.conf import settings
from django.dispatch import receiver
from requests.exceptions import RequestException
from courseware.models import SCORE_CHANGED

log = logging.getLogger("edx.grading_provider")


@receiver(SCORE_CHANGED)
def score_change_handler(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Consume signals that indicate score changes. See the definition of
    courseware.models.SCORE_CHANGED for a description of the signal.
    Used by third party application for grading using third party algorithms
    """

    points_possible = kwargs.get('points_possible', None)
    points_earned = kwargs.get('points_earned', None)
    user_id = kwargs.get('user_id', None)
    course_id = kwargs.get('course_id', None)
    usage_id = kwargs.get('usage_id', None)

    if None in (usage_id, course_id, user_id, points_earned, points_possible):
        log.error(
            "Grading Service: Required signal parameter is None. "
            "points_possible: %s, points_earned: %s, user_id: %s, "
            "course_id: %s, usage_id: %s",
            points_possible, points_earned, user_id, course_id, usage_id
        )
        return

    data = json.dumps({
        'points_possible': points_possible,
        'points_earned': points_earned,
        'user_id': user_id,
        'course_id': course_id,
        'usage_id': usage_id,
    })

    try:
        headers = {'content-type': 'application/json'}
        requests.post(settings.GRADING_SERVICE_API, data=data, headers=headers)
    except RequestException:
        log.exception("Grading Service: Error when sending grade.")
