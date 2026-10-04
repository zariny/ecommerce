import json, logging
from authentication.middleware import AbstractHybridMiddleware
from sandbox.urls import GRAPHQL_API_URLS

logger = logging.getLogger("graphql.requests")


class GraphQLLoggingMiddleware(AbstractHybridMiddleware):
    def __call__(self, request):
        self._log_request(request)
        return self.get_response(request)

    async def __acall__(self, request):
        self._log_request(request)
        return await self.get_response(request)

    def _log_request(self, request):
        if request.path.startswith(GRAPHQL_API_URLS) and request.method == "POST":
            try:
                body = json.loads(request.body)

                logger.info(
                    "GraphQL request",
                    extra={
                        "query": body.get("query"),
                        "variables": body.get("variables"),
                    },
                )
            except json.JSONDecodeError, UnicodeDecodeError:
                pass
