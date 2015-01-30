from oslo_context import context
import webob.dec

from oslo_middleware import base


class RequestIdMiddleware(base.Middleware):
    """
    It ensures to assign request ID for each HTTP request and set it to
    request environment. The request ID is also added to HTTP response.

    [filter:request_id]
    paste.filter_factory = request_id_middleware.middleware:RequestIdMiddleware.factory
    env_request_id = custom_env_request_id
    resp_header_request_id = custom-x-request-id
    """
    @classmethod
    def factory(cls, global_conf, 
    		env_request_id='x_request_id',
    		resp_header_request_id = 'x-request-id'
    		):

        cls.env_request_id = env_request_id
        cls.resp_header_request_id = resp_header_request_id
        return cls

    @webob.dec.wsgify
    def __call__(self, req):
        req_id = context.generate_request_id()
        req.environ[self.env_request_id] = req_id
        response = req.get_response(self.application)
        if self.resp_header_request_id not in response.headers:
            response.headers.add(self.resp_header_request_id, req_id)
        return response