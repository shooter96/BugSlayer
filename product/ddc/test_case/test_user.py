import pytest
from common.logger import get_logger
logger = get_logger(__name__)

@pytest.fixture(scope="class")
def setup_class_fixture(request, setup_browser):
    """
    类级别的 fixture，用于初始化测试类

    Args:
        request: pytest request 对象
        setup_browser: 浏览器环境 fixture（来自 conftest.py）
    """
    config, page = setup_browser

    # 将属性设置到测试类上
    request.cls.config = config
    request.cls.page = page
    request.cls.login_data_dict = {}

    logger.info(f"🚀 TestLogin 类初始化完成")
    logger.info(f"🖥️ 浏览器页面: {page}")

    yield
    # 测试类清理逻辑
    logger.info(f"🧹 TestLogin 类清理完成")


# ============ 类级别参数化（当前方案）============
# 优势：所有测试方法共享相同的参数化配置
@pytest.mark.parametrize(
    'setup_browser',  # ← 参数1：要参数化的 fixture 名称
    [{'port': 442},  # ← 参数2：参数值列表
     # {'port': 443}
     ], indirect=True)  # ← 参数3：间接参数化（重要！,表示参数要传递给 fixture，而不是直接传给测试函数）
@pytest.mark.usefixtures("setup_class_fixture")
class TestUser:
    """
    测试登录功能（类级别参数化）

    执行流程:
    1. TestLogin 类开始执行
    2. setup_class_fixture 自动运行
    3. 调用 setup_browser fixture，初始化浏览器
    4. 设置 cls.config 和 cls.page（类属性）
    5. yield - 开始执行测试方法
    6. test_login_yaml() 使用 self.page 和 self.config
    7. test_login_success() 使用 self.page 和 self.config
    8. 所有测试完成后，yield 后的清理代码执行
    9. TestLogin 类结束
    """

    @pytest.mark.critical
    def test_login_yaml(self):
        """
        使用env_config.yaml中的用户信息登录

        该测试会针对类级别参数化的每个端口运行一次
        """
        # 使用类属性中的配置和页面对象
        login_info = self.config.get('server', [{}])[0]
        current_url = login_info.get('url', 'N/A')

        logger.info(f"🖥️ 服务器信息: {self.config}")
        logger.info(f"🌐 准备登录到: {current_url}")

        # 导航到登录页面
        url = login_info.get('url')
        self.page.goto(url)

        # 执行登录操作
        result = login_page.login_to_system(self.page, login_info)
        assert result, f"登录失败 - URL: {current_url}"
        logger.info(f"✅ 登录成功 - URL: {current_url}")

