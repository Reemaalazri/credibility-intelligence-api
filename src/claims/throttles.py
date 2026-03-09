from rest_framework.throttling import UserRateThrottle


class ScoreRateThrottle(UserRateThrottle):
    scope = "score"
