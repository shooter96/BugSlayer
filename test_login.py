from pathlib import Path

from common.data_manager import DataManager
from playwright.sync_api import expect
import pytest
from common.logger import get_logger
from pages import login_page

logger = get_logger(__name__)


def test_login_success(setup_browser):
    """
    测试用户登录功能

    Args:
        setup_browser: 浏览器环境 fixture，包含 page, config 等对象
    """
    # 获取浏览器环境对象
    url,config, page = setup_browser
    login_info = config.get('server', [{}])[0]  # 获取第一个服务器配置
    logger.info(f"🖥️ 服务器信息: {config}")
    # 执行登录操作
    result = login_page.login_to_system(page, login_info)
    assert result