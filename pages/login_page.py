from common.logger import get_logger
from playwright.sync_api import Page, sync_playwright, TimeoutError as PlaywrightTimeoutError

"""
登录模块:
    1.setup_browser:        设置浏览器环境函数
    2.access_https_page:    访问 HTTPS 页面函数
    3.create_https_page:    通过浏览器对象创建 HTTPS 页面函数（区别于 access_https_page，该函数用于在已有一个https页面状态下创建新页面）
    4.login_to_system:      登录系统函数
    5.login_to_80_system:   登录 80 端口系统函数
    6.log_out:              退出登录函数（注意，该函数不包括退出80端口的登录）
    7.cleanup:              清理浏览器环境函数（包括关闭浏览器、删除所有cookies等）
"""
logger = get_logger(__name__)
def setup_browser(converted_crt_path, converted_key_path, config, browser_type=None):
    """
    设置浏览器环境
    
    Args:
        config (dict): 配置信息
        browser_type (str, optional): 浏览器类型，支持 'chromium', 'firefox', 'webkit'
    
    Returns:
        tuple: (playwright, browser, context, page)
    """
    playwright = sync_playwright().start()
    
    # 确定要使用的浏览器类型
    if browser_type is None:
        browser_type = config.get('browser_type', 'chromium')
    
    # 根据浏览器类型启动对应的浏览器
    if browser_type == 'firefox':
        browser = playwright.firefox.launch(
            headless=config['headless'],
            slow_mo=config['slow_mo']
        )
    elif browser_type == 'webkit':
        browser = playwright.webkit.launch(
            headless=config['headless'],
            slow_mo=config['slow_mo']
        )
    elif browser_type == 'msedge':
        browser = playwright.chromium.launch(
            headless=config['headless'],
            slow_mo=config['slow_mo'],
            channel="msedge"
        )
    else:  # 默认使用chromium
        browser = playwright.chromium.launch(
            headless=config['headless'],
            slow_mo=config['slow_mo']
        )
    
    with open(converted_crt_path, 'rb') as f:
        ca_cert = f.read()
    
    with open(converted_key_path, 'rb') as f:
        ca_key = f.read()
    
    context = browser.new_context(
        ignore_https_errors=True,
        viewport={'width': 1920, 'height': 1080},
        client_certificates=[{
            "origin": config['url'],
            "cert" : ca_cert,
            "key" : ca_key
        }]
    )
    
    context.tracing.start(
        screenshots=True, 
        snapshots=True, 
        sources=True
    )
    
    page = context.new_page()
    return playwright, browser, context, page

def access_https_page(page: Page, config, url=None):
    """
    访问HTTPS页面并处理证书警告
    
    功能:
        - 访问指定的HTTPS页面
        - 处理页面加载超时异常
        - 记录访问状态和结果到日志
    
    Args:
        page (Page): Playwright页面对象，用于执行页面导航操作
        config (dict): 配置信息字典，包含默认URL等配置项
        url (str, optional): 要访问的具体URL地址。如果未提供，则使用config中的url配置
    
    Returns:
        bool: 页面访问结果
            - True: 页面访问成功或超时但继续执行
            - False: 页面访问失败（发生非超时异常）
    """
    if not url:
        url = config['url']
        
    logger.info(f"1. 正在访问 {url}...")
    try:
        page.goto(url)
        logger.info("   ✅ 页面加载成功")
        
    except PlaywrightTimeoutError:
        logger.warning("   ⚠️  页面加载超时，尝试继续执行...")
    except Exception as e:
        logger.error(f"   ❌ 访问页面失败: {e}")
        return False
        
    return True

def create_https_page(browser, converted_crt_path, converted_key_path, config, url=None):
    """
    通过浏览器对象创建HTTPS页面
    
    功能:
        - 从已有浏览器对象创建新的HTTPS页面上下文
        - 配置客户端证书用于HTTPS双向认证
        - 设置视口大小为1920x1080
        - 忽略HTTPS证书错误
        - 导航到指定URL并返回新页面
    
    Args:
        browser: Playwright浏览器对象，用于创建新的页面上下文
        converted_crt_path (str): 客户端证书文件路径（CRT格式）
        converted_key_path (str): 客户端私钥文件路径（KEY格式）
        config (dict): 配置信息字典，包含默认URL等配置项
        url (str, optional): 要访问的具体URL地址。如果未提供，则使用config中的url配置
    
    Returns:
        Page/None: 新创建的页面对象
            - Page对象: 页面创建和导航成功
            - None: 创建过程中发生异常
    
    注意:
        - 该函数区别于access_https_page，用于在已有浏览器状态下创建新页面
        - 需要配置客户端证书进行HTTPS双向认证
        - 自动忽略HTTPS证书错误，适用于自签名证书场景
    """
    if not url:
        url = config['url']
    try:
        # 读取证书文件
        with open(converted_crt_path, 'rb') as f:
            ca_cert = f.read()
        
        with open(converted_key_path, 'rb') as f:
            ca_key = f.read()
        

        context = browser.new_context(
            ignore_https_errors=True,
            viewport={'width': 1920, 'height': 1080},
            client_certificates=[{
                "origin": url,
                "cert" : ca_cert,
                "key" : ca_key
            }]
        )

        new_page = context.new_page()
        new_page.goto(url)
        return new_page
    except Exception as e:
        logger.error(f"   ❌ 创建HTTPS页面失败: {e}")
        return None

def login_to_system(page: Page, username=None, password=None):
    """
    登录系统
    
    功能:
        - 自动识别并填写用户名输入框
        - 自动识别并填写密码输入框
        - 自动识别并点击登录按钮
        - 支持多种选择器策略，适配不同前端框架
        - 记录详细的登录操作日志
    
    Args:
        page: Playwright页面对象，用于执行登录操作
        username (str, optional): 用户名，如果未提供则需要在调用前设置
        password (str, optional): 密码，如果未提供则需要在调用前设置
    
    Returns:
        bool: 登录操作结果
            - True: 用户名、密码输入和登录按钮点击均成功
            - False: 任一环节失败（找不到输入框或登录按钮）
    
    实现细节:
        - 使用多种CSS选择器策略定位元素，提高兼容性
        - 用户名选择器包含：type、name、id、placeholder等多种属性
        - 密码选择器包含：type、name、id、placeholder等多种属性
        - 登录按钮选择器包含：submit类型、文本内容等多种策略
        - 每个元素查找超时时间为3秒
        - 登录完成后等待2秒确保页面加载
    
    注意:
        - 该函数使用智能选择器匹配，适配多种前端框架
        - 密码在日志中以星号显示，保证安全性
        - 登录完成后需要额外的等待时间确保页面完全加载
    """        
    logger.info("3. 等待登录页面...")
    page.wait_for_timeout(1000)
    
    # 用户名输入
    username_selectors = [
        "input[type='text']", "input[name='username']", "input[id='username']",
        "input[placeholder*='用户']", "input[placeholder*='username']",
        "#username", "[name='username']"
    ]
    
    username_input = None
    for selector in username_selectors:
        try:
            username_input = page.locator(selector).first
            if username_input.is_visible(timeout=3000):
                break
        except:
            continue
    
    if username_input:
        username_input.fill(username)
        logger.info(f"   ✅ 输入用户名: {username}")
    else:
        logger.error("   ❌ 未找到用户名输入框")
        return False
    
    # 密码输入
    password_selectors = [
        "input[type='password']", "input[name='password']", "input[id='password']",
        "input[placeholder*='密码']", "input[placeholder*='password']",
        "#password", "[name='password']"
    ]
    
    password_input = None
    for selector in password_selectors:
        try:
            password_input = page.locator(selector).first
            if password_input.is_visible(timeout=3000):
                break
        except:
            continue
    
    if password_input:
        password_input.fill(password)
        logger.info(f"   ✅ 输入密码: {'*' * len(password)}")
    else:
        logger.error("   ❌ 未找到密码输入框")
        return False
    
    # 登录按钮
    login_selectors = [
        "button[type='submit']", "button[type='button']", "input[type='submit']", "button:has-text('登录')",
        "button:has-text('Login')", "text=登录", "text=Login", "#loginButton",
        "[type='submit']"
    ]
    
    login_button = None
    for selector in login_selectors:
        try:
            login_button = page.locator(selector).first
            if login_button.is_visible(timeout=3000):
                break
        except:
            continue
    
    if login_button:
        login_button.click()
        logger.info("   ✅ 点击登录按钮")

    else:
        logger.error("   ❌ 未找到登录按钮")
        return False
    
    # # 等待登录完成
    # page.wait_for_timeout(2000)
    return True

def login_to_80_system(page: Page, config, username=None, password=None):
    """
    登录80端口系统
    
    功能:
        - 专门针对80端口系统的登录流程
        - 自动识别并填写用户名输入框
        - 自动识别并填写密码输入框
        - 自动识别并点击登录按钮（基于li元素）
        - 支持从config配置中读取默认用户名密码
        - 记录详细的登录操作日志
    
    Args:
        page: Playwright页面对象，用于执行登录操作
        config (dict): 配置信息字典，包含默认用户名密码等配置项
        username (str, optional): 用户名，如果未提供则使用config中的username配置
        password (str, optional): 密码，如果未提供则使用config中的password配置
    
    Returns:
        bool: 登录操作结果
            - True: 用户名、密码输入和登录按钮点击均成功
            - False: 任一环节失败（找不到输入框或登录按钮）
    
    实现细节:
        - 用户名和密码输入框的选择器与login_to_system相同
        - 登录按钮选择器专门针对80端口系统的li元素设计
        - 包含title属性和onclick事件的选择器
        - 每个元素查找超时时间为3秒
        - 登录完成后等待2秒确保页面加载
    
    注意:
        - 该函数专门针对80端口系统的特殊登录界面
        - 登录按钮基于li元素而非标准的button或input元素
        - 密码在日志中以星号显示，保证安全性
        - 如果未提供用户名密码，会自动从config配置中读取
    """
    if not username:
        username = config['username']
    if not password:
        password = config['password']
        
    logger.info("3. 等待登录页面...")
    page.wait_for_timeout(1000)
    
    # 用户名输入
    username_selectors = [
        "input[type='text']", "input[name='username']", "input[id='username']",
        "input[placeholder*='用户']", "input[placeholder*='username']",
        "#username", "[name='username']"
    ]
    
    username_input = None
    for selector in username_selectors:
        try:
            username_input = page.locator(selector).first
            if username_input.is_visible(timeout=3000):
                break
        except:
            continue
    
    if username_input:
        username_input.fill(username)
        logger.info(f"   ✅ 输入用户名: {username}")
    else:
        logger.error("   ❌ 未找到用户名输入框")
        return False
    
    # 密码输入
    password_selectors = [
        "input[type='password']", "input[name='password']", "input[id='password']",
        "input[placeholder*='密码']", "input[placeholder*='password']",
        "#password", "[name='password']"
    ]
    
    password_input = None
    for selector in password_selectors:
        try:
            password_input = page.locator(selector).first
            if password_input.is_visible(timeout=3000):
                break
        except:
            continue
    
    if password_input:
        password_input.fill(password)
        logger.info(f"   ✅ 输入密码: {'*' * len(password)}")
    else:
        logger.error("   ❌ 未找到密码输入框")
        return False
    
    # 登录按钮点击
    login_button_selectors = [
        "li.user_main_r[title='用户登录'][onclick*='login']",
        "li.user_main_r",
        "li[title='用户登录']",
        "li[onclick*='login']"
    ]
    
    login_button = None
    for selector in login_button_selectors:
        try:
            login_button = page.locator(selector).first
            if login_button.is_visible(timeout=3000):
                break
        except:
            continue
    
    if login_button:
        login_button.click()
        logger.info("   ✅ 点击登录按钮")
        # 等待登录完成
        page.wait_for_timeout(2000)
    else:
        logger.error("   ❌ 未找到登录按钮")
        return False
    
    return True

def log_out(page, port="443"):
    """
    退出443/442端口系统登录
    
    功能:
        - 根据端口号选择对应的退出按钮进行点击
        - 支持443端口和442端口的退出操作
        - 自动点击"退出"按钮完成登出
        - 记录操作日志和错误信息
    
    Args:
        page: Playwright页面对象，用于执行退出操作
        port (str): 端口号，支持"443"和"442"，默认为"443"
    
    Returns:
        bool: 退出操作结果
            - True: 退出按钮点击成功
            - False: 端口号错误或操作失败
    
    实现细节:
        - 443端口使用选择器"#ext-gen90"
        - 442端口使用选择器"#ext-gen93"
        - 点击退出按钮后等待1秒确保操作完成
        - 使用get_by_role定位"退出"按钮
        - 异常内部处理，不抛出异常
    
    注意:
        - 仅支持443和442端口，其他端口会记录错误日志
        - 使用动态ID选择器，可能存在兼容性问题
        - 异常被捕获并返回False，不中断程序执行
    """
    try:
        if port == "443":
            page.locator("#ext-gen90").click()
        elif port == "442":
            page.locator("#ext-gen93").click()
        else :
            logger.error("端口号错误")
            return False
        page.wait_for_timeout(1000)
        
        # page.locator("#content_iframe").content_frame.get_by_role("button", name="退出").click()
        page.get_by_role("button", name="退出").click()
        
        return True
    except:
        return False

def cleanup(playwright, browser, context):
    """
    清理Playwright浏览器资源
    
    功能:
        - 关闭浏览器实例
        - 停止Playwright对象
        - 确保资源被正确释放，避免内存泄漏
        - 记录清理过程中的错误信息
    
    Args:
        playwright: Playwright对象，用于停止Playwright实例
        browser: 浏览器对象，用于关闭浏览器
        context: 浏览器上下文对象，用于停止追踪
    
    Returns:
        None: 无返回值，函数执行清理操作
    
    
    注意:
        - 函数设计为幂等操作，重复调用不会导致问题
        - 所有异常都被捕获并记录，不会抛出异常中断程序
        - 建议在所有Playwright操作完成后调用此函数
    """        
    try:
        if browser:
            browser.close()
    except Exception as e:
        logger.error(f"关闭浏览器时发生错误: {e}")
        
    try:
        if playwright:
            playwright.stop()
    except Exception as e:
        logger.error(f"停止Playwright时发生错误: {e}")