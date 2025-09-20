"""
Custom exception classes for the Agno Blog application
"""


class BlogApplicationError(Exception):
    """Base exception for blog application"""

    def __init__(
        self, message: str, error_code: str = None
    ):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ContentExtractionError(BlogApplicationError):
    """Error during content extraction"""

    def __init__(self, message: str, url: str = None):
        self.url = url
        super().__init__(
            message, "content_extraction_failed"
        )


class TemplateUpdateError(BlogApplicationError):
    """Error during template update"""

    def __init__(
        self, message: str, template_id: str = None
    ):
        self.template_id = template_id
        super().__init__(message, "template_update_failed")


class BlogPostNotFoundError(BlogApplicationError):
    """Error when blog post is not found"""

    def __init__(self, message: str, post_id: str = None):
        self.post_id = post_id
        super().__init__(message, "blog_post_not_found")


class TemplateNotFoundError(BlogApplicationError):
    """Error when template is not found"""

    def __init__(
        self, message: str, template_id: str = None
    ):
        self.template_id = template_id
        super().__init__(message, "template_not_found")


class AgentProcessingError(BlogApplicationError):
    """Error during agent processing"""

    def __init__(
        self, message: str, agent_name: str = None
    ):
        self.agent_name = agent_name
        super().__init__(message, "agent_processing_failed")
