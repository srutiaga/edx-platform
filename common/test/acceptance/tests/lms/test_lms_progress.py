# -*- coding: utf-8 -*-
"""
End-to-end tests for the LMS.
"""
from textwrap import dedent
from ..helpers import UniqueCourseTest, load_data_str
from ...pages.studio.auto_auth import AutoAuthPage
from ...pages.lms.progress import ProgressPage
from ...pages.lms.problem import ProblemPage
from ...pages.lms.courseware import CoursewarePage
from ...pages.lms.course_nav import CourseNavPage
from ...fixtures.course import CourseFixture, XBlockFixtureDesc
from ...fixtures.grading import GradingConfigFixture


class ProgressTest(UniqueCourseTest):
    """
    Test courseware with multiple verticals
    """
    USERNAME = "STUDENT_TESTER"
    EMAIL = "student101@example.com"

    def setUp(self):
        super(ProgressTest, self).setUp()

        self.progress_page = ProgressPage(self.browser, self.course_id)

        # Install a course with sections/problems, tabs, updates, and handouts
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        problem = dedent("""
            <problem markdown="null">
                <text>
                    <p>
                        Given the data in Table 7 <clarification>Table 7: "Example PV Installation Costs",
                        Page 171 of Roberts textbook</clarification>, compute the ROI
                        <clarification>Return on Investment <strong>(per year)</strong></clarification> over 20 years.
                    </p>
                    <numericalresponse answer="6.5">
                        <textline label="Enter the annual ROI" trailing_text="%" />
                    </numericalresponse>
                </text>
            </problem>
        """)

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Section 1').add_children(
                XBlockFixtureDesc('sequential', 'Test Subsection 1').add_children(
                    XBlockFixtureDesc(
                        'vertical', 'Test Vertical 1', metadata={'graded': True, 'format': 'Homework', 'weight': 0.5}
                    ).add_children(XBlockFixtureDesc('problem', 'Test Problem 1', data=problem)),
                ),
                XBlockFixtureDesc('sequential', 'Test Subsection 2').add_children(
                    XBlockFixtureDesc(
                        'vertical', 'Test Vertical 2', metadata={'graded': True, 'format': 'Homework', 'weight': 0.5}
                    ).add_children(XBlockFixtureDesc('problem', 'Test Problem 3', data=problem)),
                ),
                XBlockFixtureDesc('sequential', 'Test Subsection 3').add_children(
                    XBlockFixtureDesc(
                        'vertical', 'Test Vertical 3', metadata={'graded': True, 'format': 'Exam', 'weight': 1}
                    ).add_children(XBlockFixtureDesc('problem', 'Test Problem 3', data=problem)),
                ),
            ),
        ).install()

        # Auto-auth register for the course.
        AutoAuthPage(self.browser, username=self.USERNAME, email=self.EMAIL,
                     course_id=self.course_id, staff=False).visit()

        self.courseware = CoursewarePage(self.browser, self.course_id)
        self.course_nav = CourseNavPage(self.browser)

    def test_passing_grade_table(self):
        """
        1) Not passed -> no table
        2) pass 1 < passing_grade -> see table
        3) pass all -> no table
        """
        GradingConfigFixture(self.course_id, {
            'graders': [
                {
                    'type': 'Homework', 'passing_grade': 70, 'weight': 50,
                    'min_count': 0, 'drop_count': 0, 'short_label': 'HW'
                },
                {
                    'type': 'Exam', 'passing_grade': 20, 'weight': 50,
                    'min_count': 0, 'drop_count': 0, 'short_label': 'EX'
                },
            ]
        }).install()

        self.progress_page.visit()
        self.assertTrue(self.progress_page.has_passing_information_table)
        self.assertEqual(
            self.progress_page.passing_information_table.status,
            [('Homework', 'Not passed'), ('Exam', 'Not passed'), ('Total', 'Not passed')]
        )

        self.courseware.visit()
        self.course_nav.go_to_section('Test Section 1', 'Test Subsection 1')
        problem_page = ProblemPage(self.browser)
        self.assertEqual(problem_page.problem_name, 'TEST PROBLEM 1')
        problem_page.fill_answer("6.5")
        problem_page.click_check()
        self.assertTrue(problem_page.is_correct())

        self.progress_page.visit()
        self.assertTrue(self.progress_page.has_passing_information_table)
        self.assertEqual(
            self.progress_page.passing_information_table.status,
            [('Homework', 'Not passed'), ('Exam', 'Not passed'), ('Total', 'Not passed')]
        )

        self.courseware.visit()
        self.course_nav.go_to_section('Test Section 1', 'Test Subsection 2')
        problem_page = ProblemPage(self.browser)
        problem_page.fill_answer("6.5")
        problem_page.click_check()
        self.assertTrue(problem_page.is_correct())
        self.progress_page.visit()
        self.assertTrue(self.progress_page.has_passing_information_table)
        self.assertEqual(
            self.progress_page.passing_information_table.status,
            [('Homework', 'Passed'), ('Exam', 'Not passed'), ('Total', 'Not passed')]
        )

        self.courseware.visit()
        self.course_nav.go_to_section('Test Section 1', 'Test Subsection 3')
        problem_page = ProblemPage(self.browser)
        problem_page.fill_answer("6.5")
        problem_page.click_check()
        self.assertTrue(problem_page.is_correct())
        self.progress_page.visit()
        self.assertFalse(self.progress_page.has_passing_information_table)
