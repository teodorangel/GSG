import httpx

# Monkey-patch httpx.Client.__init__ to ignore 'app' keyword argument
_orig_httpx_init = httpx.Client.__init__
def _patched_httpx_init(self, *args, **kwargs):
    kwargs.pop('app', None)
    return _orig_httpx_init(self, *args, **kwargs)
httpx.Client.__init__ = _patched_httpx_init

# Monkey-patch FastAPI TestClient to ignore 'app' keyword argument
from fastapi.testclient import TestClient as _TestClient
_orig_testclient_init = _TestClient.__init__
def _patched_testclient_init(self, *args, **kwargs):
    kwargs.pop('app', None)
    return _orig_testclient_init(self, *args, **kwargs)
_TestClient.__init__ = _patched_testclient_init
