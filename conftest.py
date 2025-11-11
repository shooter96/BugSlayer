# import os
# import sys
import pytest
from playwright.sync_api import sync_playwright
from pathlib import Path
from common.data_manager import DataManager
from pages import login_page
from common.logger import get_logger

logger = get_logger(__name__)
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture(scope="session")
def setup_browser(request, browser_type=None):
    """
    设置浏览器环境

    Args:
        request: pytest的request对象，可以通过request.param获取参数化的值
        browser_type (str, optional): 浏览器类型，支持 'chromium', 'firefox', 'webkit'。
                                    如果为None，则使用配置中的browser_type

    Returns:
        tuple: 包含 (config, page) 的元组对象
    """
    # 加载配置文件
    config_path = str(Path(__file__).parent / "conf" / "env_config.yaml")
    config = DataManager.load_yaml(config_path)
    playwright = sync_playwright().start()

    # 确定要使用的浏览器类型
    if browser_type is None:
        browser_type = config.get('browser_type', 'chromium')

    # 准备浏览器启动参数
    launch_options = {
        'headless': config['headless'],
        'slow_mo': config['slow_mo']
    }
    
    # 如果需要客户端证书，可以通过启动参数配置（仅适用于 Chromium）
    cert_dir = Path(__file__).parent / "ssl_cert" / "hz"
    cert_file = cert_dir / "converted_client.crt"
    key_file = cert_dir / "converted_client.key"
    
    if browser_type in ['chromium', 'msedge'] and cert_file.exists() and key_file.exists():
        # 注意：这种方式需要证书文件在文件系统中可访问
        launch_options['args'] = [
            f'--client-certificate-file={cert_file}',
            f'--client-certificate-key={key_file}',
            '--ignore-certificate-errors',
            '--ignore-ssl-errors'
        ]
    
    # 根据浏览器类型启动对应的浏览器
    if browser_type == 'firefox':
        browser = playwright.firefox.launch(**launch_options)
    elif browser_type == 'webkit':
        browser = playwright.webkit.launch(**launch_options)
    elif browser_type == 'msedge':
        launch_options['channel'] = "msedge"
        browser = playwright.chromium.launch(**launch_options)
    else:  # 默认使用chromium
        browser = playwright.chromium.launch(**launch_options)

    # 创建浏览器上下文
    with open(cert_file, 'rb') as f:
        ca_cert = f.read()

    with open(key_file, 'rb') as f:
        ca_key = f.read()

    # 从request.param获取端口（通过@pytest.mark.parametrize传递）
    # 如果没有指定端口，则从配置文件读取默认端口
    if hasattr(request, 'param') and isinstance(request.param, dict):
        """
        第一个参数 key: 要获取的键名
        第二个参数 default (可选): 如果键不存在时返回的默认值
        """
        port = request.param.get('port', config["server"][0].get("port_442", 442))
    else:
        port = config["server"][0].get("port_442", 442)
    
    url = "https://" + str(config["server"][0]["ip"]) + ":" + str(port)
    context = browser.new_context(
        ignore_https_errors=True,
        viewport={'width': 1920, 'height': 1080},
        client_certificates=[{
            "origin": url,
            "cert": ca_cert,
            "key": ca_key
        }]
    )

    context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True
    )

    page = context.new_page()
    yield url,config,page
    
    # 清理资源
    try:
        # context.tracing.stop(path="trace.zip")
        context.close()
        browser.close()
        playwright.stop()
    except Exception as e:
        print(f"清理资源时出错: {e}")
@pytest.fixture(scope="session")
def login_success(setup_browser):
    """
    管理员登录fixture
    
    Args:
        setup_browser: 从setup_browser fixture获取浏览器环境
        
    Returns:
        tuple: 包含 (url, config, page) 的元组对象
    """
    # 解包setup_browser返回的元组
    url, config, page = setup_browser
    server_info = config.get('server', [{}])[0]  # 获取第一个服务器配置
    logger.info(f"🖥️ 服务器信息: {config}")
    username = server_info.get('username')
    password = server_info.get('password')
    logger.info(f"🌐 准备登录到: {url}")

    # 导航到登录页面
    page.goto(url)
    #登录系统
    login_page.login_to_system(page,username,password)
    # 返回必要的对象供测试使用
    return url, config, page


