__all__ = ['StatusTags', 'error_map']


class StatusTags:

    OK = '成功'

    # 通用错误
    UnknownError = '未知错误'
    InvalidMethodError = '无效的请求方法'
    MissingParamsError = '缺失必要的请求参数'
    InvalidParamsError = '无效的参数值'
    InvalidJsonError = '无效的JSON数据'

    # 用户相关错误
    UserNotFoundError = '用户不存在'
    UserExistsError = '用户已存在'
    UserPasswordError = '密码错误'
    AuthenticationRequiredError = '需要进行用户权限认证'
    NoPermissionsError = '没有足够的权限'

    # 数据表相关相关错误
    HostNotFoundError = '该主机不存在'
    HostExistsError = '该主机已存在'
    HostConnectError = '主机连接失败'
    ProjectNotFoundError = '该项目不存在'
    ProjectExistsError = '该项目已存在'
    SpiderClsNotFoundError = '该分类不存在'
    SpiderClsExistsError = '该分类已存在'
    SpiderClsCreateError = '该分类创建失败'
    SiteNotFoundError = '该站点不存在'
    SiteExistsError = '该站点已存在'
    SpiderNotFoundError = '该爬虫不存在'
    SpiderExistsError = '该爬虫已存在'
    SpiderCreateError = '该爬虫创建失败'

    # AioSpider Service Error
    CreateProjectError = '项目创建失败'


error_map = {
    StatusTags.OK: 0,

    StatusTags.UnknownError: 1000,
    StatusTags.InvalidMethodError: 1001,
    StatusTags.MissingParamsError: 1002,
    StatusTags.InvalidParamsError: 1003,
    StatusTags.InvalidJsonError: 1004,

    StatusTags.UserNotFoundError: 2000,
    StatusTags.UserExistsError: 2001,
    StatusTags.UserPasswordError: 2002,
    StatusTags.AuthenticationRequiredError: 2003,
    StatusTags.NoPermissionsError: 2004,

    StatusTags.HostNotFoundError: 3000,
    StatusTags.HostExistsError: 3001,
    StatusTags.HostConnectError: 3002,
    StatusTags.ProjectNotFoundError: 3003,
    StatusTags.ProjectExistsError: 3004,
    StatusTags.SpiderClsNotFoundError: 3005,
    StatusTags.SpiderClsExistsError: 3006,
    StatusTags.SpiderClsCreateError: 3007,
    StatusTags.SiteNotFoundError: 3008,
    StatusTags.SiteExistsError: 3009,
    StatusTags.SpiderNotFoundError: 30010,
    StatusTags.SpiderExistsError: 3011,
    StatusTags.SpiderCreateError: 3012,

    StatusTags.CreateProjectError: 4000,
    4001: 'File upload failed',
    4002: 'File download failed',
    4003: 'Unsupported file format',

    # 5xxx: 系统相关错误
    5000: 'Internal server error',
    5001: 'Service temporarily unavailable',
    5002: 'API rate limit exceeded',
    5003: 'API endpoint deprecated',

    # 6xxx: 第三方服务相关错误
    6000: 'Third-party service error',
    6001: 'Invalid API key',
    6002: 'API request failed',
}
