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
    config,page = setup_browser
    server_info = config.get('server', [{}])[0]  # 获取第一个服务器配置
    logger.info(f"🖥️ 服务器信息: {config}")
    # 构建登录URL和获取登录凭据
    server_ip = server_info.get('ip')
    server_port = server_info.get('port_442')
    username = server_info.get('username')
    password = server_info.get('password')
    
    login_url = f"https://{server_ip}:{server_port}"
    logger.info(f"🌐 准备登录到: {login_url}")
    
    # 导航到登录页面
    page.goto(login_url)
    # 执行登录操作
    login_page.login_to_system(page,username,password)
    #assert