# coding=UTF-8
"""Tests for enrollment from the marketing site.

The marketing site uses a button rendered by the LMS
in an iframe to allow students to enroll in a course.
"""
from mock import patch
from django.test.utils import override_settings
from django.conf import settings
from django.core.urlresolvers import reverse
from course_modes.tests.factories import CourseModeFactory
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import (
    ModuleStoreTestCase, mixed_store_config
)

# Since we don't need any XML course fixtures, use a modulestore configuration
# that disables the XML modulestore.
MODULESTORE_CONFIG = mixed_store_config(settings.COMMON_TEST_DATA_ROOT, {}, include_xml=False)


@override_settings(MODULESTORE=MODULESTORE_CONFIG)
class MarketingEnrollTest(ModuleStoreTestCase):

    def setUp(self):
        self.course = CourseFactory.create()
        self.course_key = self.course.id

    def test_course_mktg_about_coming_soon(self):
        # we should not be able to find this course
        url = reverse('mktg_about_course', kwargs={'course_id': 'no/course/here'})
        response = self.client.get(url)
        self.assertIn('Coming Soon', response.content)

    def test_course_mktg_register(self):
        response = self._load_mktg_about()
        self.assertIn('Enroll in', response.content)
        self.assertNotIn('and choose your student track', response.content)

    def test_course_mktg_register_multiple_modes(self):
        CourseModeFactory(
            mode_slug='honor',
            mode_display_name='Honor Code Certificate',
            course_id=self.course_key
        )
        CourseModeFactory(
            mode_slug='verified',
            mode_display_name='Verified Certificate',
            course_id=self.course_key
        )

        response = self._load_mktg_about()
        self.assertIn('Enroll in', response.content)
        self.assertIn('and choose your student track', response.content)

    @patch.dict(settings.FEATURES, {'IS_EDX_DOMAIN': True})
    def test_mktg_about_language_edx_domain(self):
        # Since we're in an edx-controlled domain, and our marketing site
        # supports only English, override the language setting
        # and use English.
        response = self._load_mktg_about(language='eo')
        self.assertContains(response, "Enroll in")

    @patch.dict(settings.FEATURES, {'IS_EDX_DOMAIN': False})
    def test_mktg_about_language_openedx(self):
        # If we're in an OpenEdX installation,
        # may want to support languages other than English,
        # so respect the language code.
        response = self._load_mktg_about(language='eo')
        self.assertContains(response, u"Énröll ïn".encode('utf-8'))

    def _load_mktg_about(self, language=None):
        """
        Retrieve the marketing about button (iframed into the marketing site)
        and return the HTTP response.

        Keyword Args:
            language (string): If provided, send this in the 'Accept-Language' HTTP header.

        Returns:
            Response

        """
        headers = {}
        if language is not None:
            headers['HTTP_ACCEPT_LANGUAGE'] = language

        url = reverse('mktg_about_course', kwargs={'course_id': unicode(self.course_key)})
        return self.client.get(url, **headers)