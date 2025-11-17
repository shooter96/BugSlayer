import time

import pytest
from common.logger import get_logger
from conftest import login_success
from pages import login_page
from pages.navigate import navigate_to_menu

logger = get_logger(__name__)
@pytest.mark.parametrize(
    'setup_browser',  # ← 参数1：要参数化的 fixture 名称
    [{'port': 442,"username":"admin"},  # ← 参数2：参数值列表
     # {'port': 443}
     ], indirect=True)  # ← 参数3：间接参数化（重要！,表示参数要传递给 fixture，而不是直接传给测试函数）
class TestUser:
    @pytest.mark.critical
    def test_add_user(self, login_success):
        config, page = login_success
        navigate_to_menu(page, menu_name="系统管理", product="ddc")
        time.sleep(10)
