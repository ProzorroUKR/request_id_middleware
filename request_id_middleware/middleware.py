from oslo_context import context
import webob.dec

from oslo_middleware import base


class RequestIdMiddleware(base.Middleware):
    """
    It ensures to assign request ID for each HTTP request and set it to
    request environment. The request ID is also added to HTTP response.

    [filter:request_id]
    paste.filter_factory = request_id_middleware.middleware:RequestIdMiddleware.factory
    env_client_request_id = custom_env_client_request_id
    resp_header_client_request_id = custom-x-client-request-id
    env_request_id = custom_env_request_id
    resp_header_request_id = custom-x-request-id
    """
    @classmethod
    def factory(cls, global_conf,
                env_client_request_id='x_client_request_id',
                resp_header_client_request_id='X-Client-Request-ID',
                env_request_id='x_request_id',
                resp_header_request_id='X-Request-ID'):
        cls.env_client_request_id = env_client_request_id
        cls.resp_header_client_request_id = resp_header_client_request_id
        cls.env_request_id = env_request_id
        cls.resp_header_request_id = resp_header_request_id
        return cls

    @webob.dec.wsgify
    def __call__(self, req):
        client_request_id = None
        if self.env_client_request_id in req.headers:
            client_request_id = req.headers[self.resp_header_client_request_id]
            req.environ[self.env_client_request_id] = client_request_id
        if self.resp_header_request_id in req.headers:
            req_id = req.headers[self.resp_header_request_id]
        else:
            req_id = context.generate_request_id()

        req.environ[self.env_request_id] = req_id
        response = req.get_response(self.application)
        if client_request_id:
            response.headers.add(self.resp_header_client_request_id, client_request_id)
        if self.resp_header_request_id not in response.headers:
            response.headers.add(self.resp_header_request_id, req_id)

        return response
