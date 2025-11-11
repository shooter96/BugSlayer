# test_debug.py (放在与 conftest.py 同一目录)
import pytest

def test_debug_fixture(setup_browser):
    """验证 fixture 是否工作"""
    print("测试开始执行")
    assert setup_browser is not None
    assert "page" in setup_browser
    print("测试通过!")