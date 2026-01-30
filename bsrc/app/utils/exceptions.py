
class BaseExceptions(Exception):
    def __init__(self, message):
        super(Exception).__init__(message)

class DataBaseException(BaseExceptions):
    """数据库异常"""
    pass

class PluginException(BaseExceptions):
    """插件注册异常"""
    pass

class CaptchaException(BaseExceptions):
    """验证码异常"""
    pass

class NetworkException(BaseExceptions):
    """网络请求异常"""
    pass

class RedisException(BaseExceptions):
    """Redis服务异常"""
    pass

class UnexpectedException(BaseExceptions):
    """未预期错误"""
    pass