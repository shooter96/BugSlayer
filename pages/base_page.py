from playwright.sync_api import Page, Locator, expect
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from common.logger import get_logger

logger = get_logger(__name__)

class BasePage(ABC):
    """基础页面类"""
    
    def __init__(self, page: Page):
        """
        初始化页面
        
        Args:
            page: Playwright页面对象
        """
        self.page = page

    @abstractmethod
    def navigate(self) -> None:
        """导航到页面 - 子类必须实现"""
        pass
    
    @abstractmethod
    def is_loaded(self) -> bool:
        """检查页面是否加载完成 - 子类必须实现"""
        pass
    
    def wait_for_page_load(self, timeout: int = 15000):
        """
        等待页面加载完成 - 性能优化版
        
        Args:
            timeout: 超时时间(毫秒)
        """
        logger.info(f"等待页面加载完成: {self.__class__.__name__}")
        
        # 使用domcontentloaded而不是networkidle，更快
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout//2)
            logger.info("DOM内容加载完成")
        except Exception as e:
            logger.warning(f"DOM加载超时，继续执行: {e}")
        
        # 跳过元素等待，直接检查页面是否可用
        if hasattr(self, 'page_loaded_indicator'):
            try:
                # 快速检查元素是否存在，不等待可见性
                element = self.page.locator(self.page_loaded_indicator)
                if element.count() > 0:
                    logger.info(f"页面指示器元素已找到: {self.page_loaded_indicator}")
                else:
                    logger.info(f"页面指示器元素未找到，但继续执行: {self.page_loaded_indicator}")
            except Exception as e:
                logger.warning(f"页面指示器检查失败，继续执行: {e}")
    
    def get_page_title(self) -> str:
        """获取页面标题"""
        title = self.page.title()
        logger.info(f"页面标题: {title}")
        return title
    
    def get_current_url(self) -> str:
        """获取当前URL"""
        url = self.page.url
        logger.info(f"当前URL: {url}")
        return url
    
    def refresh_page(self):
        """刷新页面"""
        logger.info("刷新页面")
        self.page.reload()
        self.wait_for_page_load()
    
    def go_back(self):
        """返回上一页"""
        logger.info("返回上一页")
        self.page.go_back()
        self.wait_for_page_load()
    
    def go_forward(self):
        """前进到下一页"""
        logger.info("前进到下一页")
        self.page.go_forward()
        self.wait_for_page_load()
    
    def scroll_to_top(self):
        """滚动到页面顶部"""
        logger.info("滚动到页面顶部")
        self.page.evaluate("window.scrollTo(0, 0)")
    
    def scroll_to_bottom(self):
        """滚动到页面底部"""
        logger.info("滚动到页面底部")
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    
    def wait_for_element(self, selector: str, timeout: int = 30000) -> Locator:
        """
        等待元素出现
        
        Args:
            selector: 元素选择器
            timeout: 超时时间(毫秒)
            
        Returns:
            Locator: 元素定位器
        """
        return self.utils.wait_for_element(selector, timeout)
    
    def click_element(self, selector: str, timeout: int = 30000) -> bool:
        """
        点击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间(毫秒)
            
        Returns:
            bool: 是否点击成功
        """
        return self.utils.safe_click(selector, timeout)
    
    def fill_text(self, selector: str, text: str, timeout: int = 30000) -> bool:
        """
        填写文本
        
        Args:
            selector: 元素选择器
            text: 要填写的文本
            timeout: 超时时间(毫秒)
            
        Returns:
            bool: 是否填写成功
        """
        return self.utils.safe_fill(selector, text, timeout)
    
    def get_element_text(self, selector: str, timeout: int = 30000) -> Optional[str]:
        """
        获取元素文本
        
        Args:
            selector: 元素选择器
            timeout: 超时时间(毫秒)
            
        Returns:
            Optional[str]: 元素文本
        """
        return self.utils.get_text(selector, timeout)
    
    def is_element_visible(self, selector: str, timeout: int = 5000) -> bool:
        """
        检查元素是否可见
        
        Args:
            selector: 元素选择器
            timeout: 超时时间(毫秒)
            
        Returns:
            bool: 元素是否可见
        """
        return self.utils.is_element_visible(selector, timeout)
    
    def take_screenshot(self, file_name: str = None):
        """
        截取页面截图
        
        Args:
            file_name: 截图文件名，为None时自动生成
        """
        if not file_name:
            from datetime import datetime
            file_name = f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        file_path = f"reports/screenshots/{file_name}"
        self.utils.take_screenshot(file_path)
    
    def assert_element_visible(self, selector: str, error_message: str = None):
        """
        断言元素可见
        
        Args:
            selector: 元素选择器
            error_message: 自定义错误信息
        """
        element = self.page.locator(selector)
        expect(element).to_be_visible()
        logger.info(f"断言成功: 元素可见 - {selector}")
    
    def assert_element_text(self, selector: str, expected_text: str, error_message: str = None):
        """
        断言元素文本
        
        Args:
            selector: 元素选择器
            expected_text: 期望的文本
            error_message: 自定义错误信息
        """
        element = self.page.locator(selector)
        expect(element).to_have_text(expected_text)
        logger.info(f"断言成功: 元素文本匹配 - {selector} = {expected_text}")
    
    def assert_page_url(self, expected_url: str, error_message: str = None):
        """
        断言页面URL
        
        Args:
            expected_url: 期望的URL
            error_message: 自定义错误信息
        """
        expect(self.page).to_have_url(expected_url)
        logger.info(f"断言成功: 页面URL匹配 - {expected_url}")
    
    def assert_page_title(self, expected_title: str, error_message: str = None):
        """
        断言页面标题
        
        Args:
            expected_title: 期望的标题
            error_message: 自定义错误信息
        """
        expect(self.page).to_have_title(expected_title)
        logger.info(f"断言成功: 页面标题匹配 - {expected_title}")

class BaseDialog(BasePage):
    """基础对话框类"""
    
    def __init__(self, page: Page, dialog_selector: str):
        """
        初始化对话框
        
        Args:
            page: Playwright页面对象
            dialog_selector: 对话框选择器
        """
        super().__init__(page)
        self.dialog_selector = dialog_selector
    
    def is_loaded(self) -> bool:
        """检查对话框是否加载完成"""
        return self.is_element_visible(self.dialog_selector)
    
    def close_dialog(self):
        """关闭对话框"""
        close_button = f"{self.dialog_selector} .close-button"
        if self.is_element_visible(close_button):
            self.click_element(close_button)
        else:
            # 尝试按ESC键关闭
            self.page.keyboard.press("Escape") 