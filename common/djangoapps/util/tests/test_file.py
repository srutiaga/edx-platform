"""
Tests for file.py
"""

from django.test import TestCase
from datetime import datetime
from django.utils.timezone import UTC
from mock import patch, Mock
from django.http import HttpRequest
from django.core.files.uploadedfile import SimpleUploadedFile
import util.file
from util.file import course_and_time_based_filename_generator, store_uploaded_file
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from django.core import exceptions


class FilenameGeneratorTestCase(TestCase):
    """
    Tests for course_and_time_based_filename_generator
    """
    NOW = datetime.strptime('1974-06-22T01:02:03', '%Y-%m-%dT%H:%M:%S').replace(tzinfo=UTC())

    def setUp(self):
        datetime_patcher = patch.object(
            util.file, 'datetime',
            Mock(wraps=datetime)
        )
        mocked_datetime = datetime_patcher.start()
        mocked_datetime.now.return_value = self.NOW
        self.addCleanup(datetime_patcher.stop)

    def test_filename_generator(self):
        self.assertEqual(
            "course_id_file_1974-06-22-010203",
            course_and_time_based_filename_generator("course/id", "file")
        )
        self.assertEqual(
            "__1974-06-22-010203",
            course_and_time_based_filename_generator("", "")
        )
        course_key = SlashSeparatedCourseKey.from_deprecated_string("foo/bar/123")
        self.assertEqual(
            "foo_bar_123_cohorted_1974-06-22-010203",
            course_and_time_based_filename_generator(course_key, "cohorted")
        )


class StoreUploadedFileTestCase(TestCase):
    """
    Tests for store_uploaded_file.
    """

    def setUp(self):
        self.request = Mock(spec=HttpRequest)
        self.request.FILES = {"uploaded_file": SimpleUploadedFile("tempfile.csv", "content")}

    def test_error_conditions(self):
        def verify_exception(expected_message):
            self.assertEqual(expected_message, error.exception.message)

        with self.assertRaises(ValueError) as error:
            store_uploaded_file(self.request, "wrong_key", [".txt", ".csv"], 1000, "stored_file")
        verify_exception("No file uploaded with key 'wrong_key'.")

        with self.assertRaises(exceptions.PermissionDenied) as error:
            store_uploaded_file(self.request, "uploaded_file", [], 1000, "stored_file")
        verify_exception("Allowed file types are ''.")

        with self.assertRaises(exceptions.PermissionDenied) as error:
            store_uploaded_file(self.request, "uploaded_file", [".xxx", ".bar"], 1000, "stored_file")
        verify_exception("Allowed file types are '.xxx', '.bar'.")

        with self.assertRaises(exceptions.PermissionDenied) as error:
            store_uploaded_file(self.request, "uploaded_file", [".csv"], 2, "stored_file")
        verify_exception("Maximum upload file size is 2 bytes.")

    def test_file_upload(self):
        file_storage, file_name = store_uploaded_file(self.request, "uploaded_file", [".csv"], 1000, "stored_file")



