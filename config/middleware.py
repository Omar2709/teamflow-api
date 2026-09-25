from django.middleware.common import CommonMiddleware


class ALBCompatibleCommonMiddleware(CommonMiddleware):
    HEALTH_CHECK_PATHS = (
        "/health/",
        "/ready/",
    )

    def process_request(self, request):
        if request.path in self.HEALTH_CHECK_PATHS:
            return None

        return super().process_request(
            request,
        )
