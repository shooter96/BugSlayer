from common.logger import get_logger
from playwright.sync_api import Page, sync_playwright, TimeoutError as PlaywrightTimeoutError
logger = get_logger(__name__)
"""
导航模块
1.navigate_to_menu导航到不同的页面，如业务管理、系统管理、统计与审计、网络管理等
2.navigate_to_business_by_name导航到指定的业务，如网卡设置、平台配置、ssh设置、防火墙设置等
"""

def navigate_to_menu(page: Page, menu_name: str, product: str = None, selectors: list = None):
    """
    通用导航函数 - 导航到指定菜单模块
    
    功能:
        - 根据菜单名称和选择器列表导航到指定模块
        - 支持自定义选择器，提供默认选择器策略
        - 智能匹配菜单元素，适配不同的前端框架
        - 记录详细的导航操作日志
    
    Args:
        page: Playwright页面对象，用于执行导航操作
        menu_name (str): 菜单名称，用于日志记录和默认选择器生成
        selectors (list, optional): 自定义CSS选择器列表，如果未提供则使用默认选择器
    
    Returns:
        bool: 导航操作结果
            - True: 成功找到并点击菜单
            - False: 未找到指定菜单
    
    实现细节:
        - 默认选择器策略：text、a:has-text、span:has-text
        - 元素查找超时时间为5秒
        - 使用.first获取第一个匹配的元素
        - 成功点击后等待1秒确保页面加载完成
    
    注意:
        - 该函数为通用导航函数，替代原有的特定菜单导航函数
        - 选择器列表按优先级顺序尝试，找到第一个可见元素即停止
        - 异常被捕获并继续尝试下一个选择器，确保鲁棒性
        - 建议优先使用包含具体菜单名称的选择器
    """
    logger.info(f"导航到{menu_name}模块...")

    if product == "sg":
        page.locator("#iframe-menu").content_frame.get_by_text(f"{menu_name}").click()
        page.wait_for_timeout(1000)
        return True
    
    # 如果没有提供选择器，使用默认选择器策略
    if selectors is None:
        selectors = [
            f"text={menu_name}",
            f"a:has-text('{menu_name}')",
            f"span:has-text('{menu_name}')"
        ]
    
    menu_element = None
    for selector in selectors:
        try:
            menu_element = page.locator(selector).first
            if menu_element.is_visible(timeout=5000):
                menu_element.click()
                logger.info(f"   ✅ 点击了{menu_name}")
                break
        except:
            continue
    
    if not menu_element:
        logger.error(f"   ❌ 未找到{menu_name}菜单")
        return False
    
    # 等待页面加载
    page.wait_for_timeout(1000)
    return True

def check_service_exists(page: Page, service_name):
    """
    检查服务是否存在于树形导航结构中
    
    功能:
        - 在树形导航面板中查找指定服务名称
        - 支持多种树形容器选择器，适配不同前端框架
        - 使用多种选择器策略定位服务元素
        - 记录详细的查找过程和结果
    
    Args:
        page: Playwright页面对象，用于执行查找操作
        service_name (str): 要查找的服务名称
    
    Returns:
        bool: 服务存在性检查结果
            - True: 服务在树形结构中找到
            - False: 服务不存在或无法找到树形容器
    
    实现细节:
        - 树形容器选择器：#ktree、.x-tree-root-ct、.x-tree-root-node
        - 容器查找超时时间：5秒
        - 服务元素选择器：span:text-is、a span、.x-tree-node-anchor span等
        - 服务查找超时时间：3秒
        - 使用.first获取第一个匹配的元素
    
    注意:
        - 函数先查找树形容器，再在容器内查找服务元素
        - 使用Playwright的text-is选择器进行精确文本匹配
        - 异常被捕获并继续尝试下一个选择器
        - 日志使用不同图标区分结果（✅存在，ℹ️不存在）
    """   
    logger.info(f"检查服务 '{service_name}' 是否存在...")
    
    # 基于导航面板的树形结构查找业务
    tree_selectors = [
        "#ktree",
        ".x-tree-root-ct",
        ".x-tree-root-node"
    ]
    
    tree_container = None
    for selector in tree_selectors:
        try:
            tree_container = page.locator(selector).first
            if tree_container.is_visible(timeout=5000):
                break
        except:
            continue
    
    if tree_container:
        # 在树形结构中查找业务名称
        service_selectors = [
            f"span:text-is('{service_name}')",
            f"a span:text-is('{service_name}')",
            f".x-tree-node-anchor span:text-is('{service_name}')",
            f"[ext:tree-node-id*='{service_name}']",
            f".app-1210 span:text-is('{service_name}')"
        ]
        
        for selector in service_selectors:
            try:
                service_item = tree_container.locator(selector).first
                if service_item.is_visible(timeout=3000):
                    logger.info(f"   ✅ 服务 '{service_name}' 已存在")
                    return True
            except:
                continue
    
    logger.info(f"   ℹ️  服务 '{service_name}' 不存在")
    return False

def navigate_to_business_by_name(page: Page, service_name, product :str = None):
    """
    根据业务名称导航到指定业务页面
    
    功能:
        - 检查服务是否存在（调用check_service_exists）
        - 在树形导航结构中查找并点击目标业务
        - 等待页面加载完成
        - 提供完整的导航流程和错误处理
    
    Args:
        page: Playwright页面对象，用于执行导航操作
        service_name (str): 要导航到的业务名称
    
    Returns:
        bool: 导航操作结果
            - True: 成功导航到目标业务页面
            - False: 导航失败（服务不存在、无法点击、页面加载超时等）
    
    实现细节:
        - 首先调用check_service_exists检查服务存在性
        - 使用相同的树形容器选择器策略：#ktree、.x-tree-root-ct、.x-tree-root-node
        - 容器查找超时时间：5秒
        - 服务元素选择器：span:text-is、a span、.x-tree-node-anchor span等
        - 服务查找超时时间：3秒
        - 点击操作超时时间：5秒
        - 页面加载等待：networkidle状态，10秒超时
    
    注意:
        - 函数依赖check_service_exists的结果，服务不存在时直接返回False
        - 使用与check_service_exists相同的选择器策略确保一致性
        - 提供详细的错误日志，使用不同图标区分错误类型
        - 成功导航后等待页面networkidle状态，确保页面完全加载
    """
    logger.info(f"导航到业务 '{service_name}'...")
    
    if product == "sg":
        page.locator("#iframe-menu").content_frame.get_by_role("link", name=f"{service_name}").click()
        page.wait_for_timeout(1000)
        return True
    # 首先检查服务是否存在
    if not check_service_exists(page, service_name):
        logger.error(f"   ❌ 业务 '{service_name}' 不存在，导航失败")
        return False
    
    # 基于导航面板的树形结构查找业务
    tree_selectors = [
        "#ktree",
        ".x-tree-root-ct", 
        ".x-tree-root-node"
    ]
    
    tree_container = None
    for selector in tree_selectors:
        try:
            tree_container = page.locator(selector).first
            if tree_container.is_visible(timeout=5000):
                break
        except:
            continue
    
    if not tree_container:
        logger.error("   ❌ 无法找到树形导航容器")
        return False
    
    # 在树形结构中查找业务名称并点击
    service_selectors = [
        f"span:text-is('{service_name}')",
        f"a span:text-is('{service_name}')",
        f".x-tree-node-anchor span:text-is('{service_name}')",
        f"[ext:tree-node-id*='{service_name}']",
        f".app-1210 span:text-is('{service_name}')"
    ]
    
    service_clicked = False
    for selector in service_selectors:
        try:
            service_item = tree_container.locator(selector).first
            if service_item.is_visible(timeout=3000):
                logger.info(f"   📍 找到业务 '{service_name}'，正在点击...")
                service_item.click(timeout=5000)
                service_clicked = True
                break
        except:
            continue
    
    if not service_clicked:
        logger.error(f"   ❌ 无法点击业务 '{service_name}'")
        return False
    
    # 等待页面加载
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
        logger.info(f"   ✅ 成功导航到业务 '{service_name}'")
        return True
    except Exception as e:
        logger.error(f"   ❌ 导航到业务 '{service_name}' 后页面加载超时: {e}")
        return False