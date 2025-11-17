import time
from pathlib import Path

from common.data_manager import DataManager
from playwright.sync_api import expect
import pytest
from common.logger import get_logger
from pages import login_page

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
    'setup_browser', # ← 参数1：要参数化的 fixture 名称
    [ {'port': 442}, # ← 参数2：参数值列表
    # {'port': 443} 
], indirect=True)  # ← 参数3：间接参数化（重要！,表示参数要传递给 fixture，而不是直接传给测试函数）
@pytest.mark.usefixtures("setup_class_fixture")
class TestLogin:
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


# ============ 函数级别参数化（备选方案）============
# 优势：每个测试方法可以独立配置不同的参数
class TestLoginFunctionLevel:
    """
    测试登录功能（函数级别参数化）
    
    每个测试方法独立配置参数，互不影响
    """
    # 加载测试数据
    login_data = login_page.get_login_data('product/ddc/test_data/login_data.json')
    login_success_data=login_data.get('login_success')

    # ========== 方法1：端口和登录数据配对（推荐）⭐ ==========
    @pytest.mark.smoke
    @pytest.mark.parametrize('setup_browser,login_info', [
        # 从 login_success_data 中提取 port 和登录数据配对
        ({'port': data['port']}, data) 
        for data in login_success_data
    ], indirect=['setup_browser'])  # 只有 setup_browser 使用 indirect
    def test_login_with_port_from_data(self, setup_browser, login_info):
        """
        方法1：从 login_data 中提取 port 传给 setup_browser
        
        该测试会运行 4 次（4条登录数据 × 1个端口）
        
        Args:
            setup_browser: 浏览器环境，端口来自 login_info['port']
            login_info: 登录数据字典 {'username': 'xxx', 'password': 'xxx', 'port': xxx}
        """
        config, page = setup_browser
        current_url = config['server'][0].get('url', 'N/A')
        
        logger.info(f"🌐 测试URL: {current_url}")
        logger.info(f"👤 登录用户: {login_info['username']}")
        
        # 导航到登录页面
        page.goto(current_url)
        
        # 使用参数化的登录信息
        login_page.login_to_system(page, {
            **config.get('server', [{}])[0],
            'username': login_info['username'],
            'password': login_info['password']
        })
        login_name=login_page.get_login_username(page)
        assert login_name == login_info['username']
        time.sleep(1)
        login_page.log_out(page,login_info["port"])


