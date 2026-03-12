from rest_framework.throttling import UserRateThrottle


# Custom throttle limiting how often users can call the claim scoring endpoint
class ScoreRateThrottle(UserRateThrottle):
    # Uses the "score" rate defined in REST_FRAMEWORK settings
    scope = "score"
    # Maximum 15 scoring requests per user per hour
    rate = "15/hour"
