from collections import OrderedDict

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect
from certificates import api as certs_api
from courseware.views import is_course_passed
from edxmako.shortcuts import render_to_response
from django.views.decorators.cache import cache_control
from django.db import transaction

from courseware import grades
from courseware.access import has_access
from courseware.courses import (
    get_studio_url, get_course_with_access,
)
from openedx.core.djangoapps.credit.api import (
    get_credit_requirement_status,
    is_user_eligible_for_credit,
    is_credit_course
)
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.locations import SlashSeparatedCourseKey

import survey.utils
import survey.views

from util.views import ensure_valid_course_key

@login_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@transaction.commit_manually
@ensure_valid_course_key
def grading_progress(request, course_id, student_id=None):
    """
    Wraps "_progress" with the manual_transaction context manager just in case
    there are unanticipated errors.
    """
    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)

    with modulestore().bulk_operations(course_key):
        with grades.manual_transaction():
            return _grading_progress(request, course_key, student_id)


def _grading_progress(request, course_key, student_id):
    """
    Unwrapped version of "progress".

    User progress. We show the grade bar and every problem score.

    Course staff are allowed to see the progress of students in their class.
    """
    course = get_course_with_access(request.user, 'load', course_key, depth=None, check_if_enrolled=True)

    # check to see if there is a required survey that must be taken before
    # the user can access the course.
    if survey.utils.must_answer_survey(course, request.user):
        return redirect(reverse('course_survey', args=[unicode(course.id)]))

    staff_access = has_access(request.user, 'staff', course)

    if student_id is None or student_id == request.user.id:
        # always allowed to see your own profile
        student = request.user
    else:
        # Requesting access to a different student's profile
        if not staff_access:
            raise Http404
        try:
            student = User.objects.get(id=student_id)
        # Check for ValueError if 'student_id' cannot be converted to integer.
        except (ValueError, User.DoesNotExist):
            raise Http404

    # NOTE: To make sure impersonation by instructor works, use
    # student instead of request.user in the rest of the function.

    # The pre-fetching of groups is done to make auth checks not require an
    # additional DB lookup (this kills the Progress page in particular).
    student = User.objects.prefetch_related("groups").get(id=student.id)

    courseware_summary = grades.progress_summary(student, request, course)
    studio_url = get_studio_url(course, 'settings/grading')
    grade_summary = grades.grade(student, request, course)

    if courseware_summary is None:
        #This means the student didn't have access to the course (which the instructor requested)
        raise Http404

    # checking certificate generation configuration
    show_generate_cert_btn = certs_api.cert_generation_enabled(course_key)

    credit_course_requirements = None
    is_course_credit = settings.FEATURES.get("ENABLE_CREDIT_ELIGIBILITY", False) and is_credit_course(course_key)
    if is_course_credit:
        requirement_statuses = get_credit_requirement_status(course_key, student.username)
        if any(requirement['status'] == 'failed' for requirement in requirement_statuses):
            eligibility_status = "not_eligible"
        elif is_user_eligible_for_credit(student.username, course_key):
            eligibility_status = "eligible"
        else:
            eligibility_status = "partial_eligible"

        paired_requirements = {}
        for requirement in requirement_statuses:
            namespace = requirement.pop("namespace")
            paired_requirements.setdefault(namespace, []).append(requirement)

        credit_course_requirements = {
            'eligibility_status': eligibility_status,
            'requirements': OrderedDict(sorted(paired_requirements.items(), reverse=True))
        }

    context = {
        'course': course,
        'courseware_summary': courseware_summary,
        'studio_url': studio_url,
        'grade_summary': grade_summary,
        'staff_access': staff_access,
        'student': student,
        'passed': is_course_passed(course, grade_summary),
        'show_generate_cert_btn': show_generate_cert_btn,
        'credit_course_requirements': credit_course_requirements,
        'is_credit_course': is_course_credit,
    }

    if show_generate_cert_btn:
        context.update(certs_api.certificate_downloadable_status(student, course_key))
        # showing the certificate web view button if feature flags are enabled.
        if settings.FEATURES.get('CERTIFICATES_HTML_VIEW', False):
            if certs_api.get_active_web_certificate(course) is not None:
                context.update({
                    'show_cert_web_view': True,
                    'cert_web_view_url': u'{url}'.format(
                        url=certs_api.get_certificate_url(user_id=student.id, course_id=unicode(course.id))
                    )
                })
            else:
                context.update({
                    'is_downloadable': False,
                    'is_generating': True,
                    'download_url': None
                })

    with grades.manual_transaction():
        response = render_to_response('courseware/progress.html', context)

    return response