"""
Views for user API
"""
from courseware.model_data import FieldDataCache
from courseware.module_render import get_module_for_descriptor
from util.json_request import JsonResponse

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect

from rest_framework import generics, permissions, views
from rest_framework.authentication import OAuth2Authentication, SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated


from courseware import access
from courseware.views import get_current_child, save_position_from_leaf

from opaque_keys.edx.keys import CourseKey, UsageKey

from student.models import CourseEnrollment, User
from student.roles import CourseBetaTesterRole
from student import auth

from xmodule.modulestore.django import modulestore


from .serializers import CourseEnrollmentSerializer, UserSerializer


STANDARD_HIERARCHY_DEPTH = 2


class IsUser(permissions.BasePermission):
    """
    Permission that checks to see if the request user matches the User models
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj


class UserDetail(generics.RetrieveAPIView):
    """
    **Use Case**

        Get information about the specified user and
        access other resources the user has permissions for.

        Users are redirected to this endpoint after logging in.

        You can use the **course_enrollments** value in
        the response to get a list of courses the user is enrolled in.

    **Example request**:

        GET /api/mobile/v0.5/users/{username}

    **Response Values**

        * id: The ID of the user.

        * username: The username of the currently logged in user.

        * email: The email address of the currently logged in user.

        * name: The full name of the currently logged in user.

        * course_enrollments: The URI to list the courses the currently logged
          in user is enrolled in.
    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, IsUser)
    queryset = (
        User.objects.all()
        .select_related('profile', 'course_enrollments')
    )
    serializer_class = UserSerializer
    lookup_field = 'username'


@authentication_classes((OAuth2Authentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
class UserCourseStatus(views.APIView):
    """
    Endpoints for getting and setting meta data
    about a user's status within a given course.
    Supports get and post
    """

    def _last_visited_module_id(self, request, course_key, course):
        """
        Returns the id of the last module visited by the current user in the given course.
        If there is no such visit returns the default (the first item deep enough down the course tree)
        """
        field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
            course_key, request.user, course, depth=2)

        course_module = get_module_for_descriptor(request.user, request, course, field_data_cache, course_key)
        current = course_module

        for i in range(0, STANDARD_HIERARCHY_DEPTH):
            child = None
            if current:
                child = get_current_child(current, min_depth=STANDARD_HIERARCHY_DEPTH - i)

            if next:
                current = child
            else:
                break

        return current

    def _process_arguments(self, request, username, course_id, body):
        """
        Checks and processes the arguments to our endpoint
        then passes the processed and verified arguments on to something that
        does the work specific to the individual case
        """
        if username != request.user.username:
            return HttpResponseForbidden("Unauthorized")
        course_key = None
        if course_id:
            course_key = CourseKey.from_string(course_id)
            course = modulestore().get_course(course_key, depth=None)
        else:
            return HttpResponseBadRequest("Required argument 'course_id' not specified")

        if not course_key:
            return HttpResponseBadRequest("Course key could not be extracted for course_id")
        if not course:
            return HttpResponseBadRequest("Course not found")

        return body(course_key, course)

    def get(self, request, username, course_id):
        """
        **Use Case**

            Get meta data about user's status within a specific course

        **Example request**:

            GET /api/mobile/v0.5/users/{username}/course_status_info/{course_id}

        **Response Values**

        * last_visited_module_id: The id of the last module visited by the user in the given course

        """
        def body(course_key, course):
            """
            Returns the course status as Json
            """
            current_module = self._last_visited_module_id(request, course_key, course)
            if current_module:
                return JsonResponse({"last_visited_module_id": unicode(current_module.location)})
            else:
                # We shouldn't end up in this case, but if we do, return something reasonable
                return JsonResponse({"last_visited_module_id": unicode(course.location)})

        return self._process_arguments(request, username, course_id, body)

    def _update_last_visited_module_id(self, request, course_key, course, module_key):
        """
        Saves the module id
        """
        field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
            course_key, request.user, course, depth=2)
        module = modulestore().get_item(module_key)
        course_module = get_module_for_descriptor(request.user, request, module, field_data_cache, course_key)
        if course_module:
            save_position_from_leaf(request.user, request, field_data_cache, course_module)
            return HttpResponse(status=204)
        else:
            return HttpResponseBadRequest("Could not find module for module_id")

    def post(self, request, username, course_id):
        """
        **Use Case**

            Update meta data about user's status within a specific course

        **Example request**:

            POST /api/mobile/v0.5/users/{username}/course_status_info/{course_id}
            body:
                last_visited_module_id={module_id}

        **Response Values**

        A successful response returns HTTP status code 204 and no content.

        """
        def body(course_key, course):
            """
            Updates the course_status once the arguments are checked
            """
            module_id = request.POST.get("last_visited_module_id")

            if module_id:
                module_key = UsageKey.from_string(module_id)
                return self._update_last_visited_module_id(request, course_key, course, module_key)
            else:
                # The arguments are optional, so if there's no argument just succeed
                return HttpResponse(status=204)

        return self._process_arguments(request, username, course_id, body)


class UserCourseEnrollmentsList(generics.ListAPIView):
    """
    **Use Case**

        Get information about the courses the currently logged in user is
        enrolled in.

    **Example request**:

        GET /api/mobile/v0.5/users/{username}/course_enrollments/

    **Response Values**

        * created: The date the course was created.
        * mode: The type of certificate registration for this course:  honor or
          certified.
        * is_active: Whether the course is currently active; true or false.
        * course: A collection of data about the course:

          * course_about: The URI to get the data for the course About page.
          * course_updates: The URI to get data for course updates.
          * number: The course number.
          * org: The organization that created the course.
          * video_outline: The URI to get the list of all vides the user can
            access in the course.
          * id: The unique ID of the course.
          * latest_updates:  Reserved for future use.
          * end: The end date of the course.
          * name: The name of the course.
          * course_handouts: The URI to get data for course handouts.
          * start: The data and time the course starts.
          * course_image: The path to the course image.
    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, IsUser)
    queryset = CourseEnrollment.objects.all()
    serializer_class = CourseEnrollmentSerializer
    lookup_field = 'username'

    def get_queryset(self):
        qset = self.queryset.filter(
            user__username=self.kwargs['username'], is_active=True
        ).order_by('created')
        return mobile_course_enrollments(qset, self.request.user)


@api_view(["GET"])
@authentication_classes((OAuth2Authentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def my_user_info(request):
    """
    Redirect to the currently-logged-in user's info page
    """
    return redirect("user-detail", username=request.user.username)


def mobile_course_enrollments(enrollments, user):
    """
    Return enrollments only if courses are mobile_available (or if the user has
    privileged (beta, staff, instructor) access)

    :param enrollments is a list of CourseEnrollments.
    """
    for enr in enrollments:
        course = enr.course

        # Implicitly includes instructor role via the following has_access check
        role = CourseBetaTesterRole(course.id)

        # The course doesn't always really exist -- we can have bad data in the enrollments
        # pointing to non-existent (or removed) courses, in which case `course` is None.
        if course and (course.mobile_available or auth.has_access(user, role) or access.has_access(user, 'staff', course)):
            yield enr
