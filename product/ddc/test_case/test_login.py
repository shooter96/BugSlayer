import time
from pathlib import Path

from common.data_manager import DataManager
from playwright.sync_api import expect
import pytest
from common.logger import get_logger
from pages import login_page

logger = get_logger(__name__)


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
        
        try:
            # 登录
            login_page.login_to_system(page, {
                "url": current_url,
                'username': login_info['username'],
                'password': login_info['password']
            })
            
            # 验证登录
            login_name = login_page.get_login_username(page)
            
            # 写入日志并断言
            if login_name != login_info['username']:
                error_msg = f"用户名不匹配: 期望={login_info['username']}, 实际={login_name}"
                logger.error(f"❌ {error_msg}")
                assert False, error_msg
             # 没有异常，代码执行完毕 → PASSED
            logger.info(f"✅ 登录成功 - {login_name}")
            
        except Exception as e:
            logger.error(f"❌ 测试失败: {e}")
            raise  # 标记测试失败，继续下一个用例
            
        finally:
            # 清理：退出登录
            try:
                login_page.log_out(page, login_info["port"])
                logger.info(f"🚪 已退出登录")
            except:
                logger.warning(f"⚠️ 退出登录失败，清除会话")
                page.context.clear_cookies()  # 强制清除会话


