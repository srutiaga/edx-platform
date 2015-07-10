from lms.djangoapps.courseware.tabs import EnrolledTab


class GradingProgressTab(EnrolledTab):
    """
    The course grading progress view.
    """
    type = 'grading_progress'
    title = 'Grading Progress'
    view_name = 'grading_progress'
    is_dynamic = True