"""
Tests of the LMS XBlock Mixin
"""

from xblock.validation import ValidationMessage
from xmodule.tests.xml import factories as xml
from xmodule.tests.test_split_test_module import SplitTestModuleTest


class SplitTestModuleFactory(xml.XmlImportFactory):
    """
    Factory for generating SplitTestModules for testing purposes
    """
    tag = 'split_test'


class XBlockValidationTest(SplitTestModuleTest):
    """
    Unit tests for XBlock validation
    """
    def test_validate(self):
        """
        Test the validation messages produced for different split test configurations.
        """
        split_test_module = self.split_test_module

        def verify_validation_message(message, expected_message, expected_message_type):
            """
            Verify that the validation message has the expected validation message and type.
            """
            self.assertEqual(message.text, expected_message)
            self.assertEqual(message.type, expected_message_type)

        # Verify the messages for an unconfigured user partition
        split_test_module.group_access[999] = {0}
        validation = split_test_module.validate()
        self.assertEqual(len(validation.messages), 1)
        verify_validation_message(
            validation.summary,
            u"This xblock refers to a deleted content group configuration.",
            ValidationMessage.ERROR,
        )
