#!/usr/bin/env python3
"""
测试配置加载
"""

from pathlib import Path
# from common.data_manager import DataManager
#
# def test_config():
#     config_path = str(Path(__file__).parent / "conf" / "env_config.yaml")
#     config = DataManager.load_yaml(config_path)
#
#     print(f"📁 配置文件路径: {config_path}")
#     print(f"📄 配置内容: {config}")
#     print(f"📊 配置类型: {type(config)}")
#
#     if config:
#         print("✅ 配置加载成功")
#         if 'server' in config:
#             print(f"🖥️ 服务器配置: {config['server']}")
#         if 'browser_type' in config:
#             print(f"🌐 浏览器类型: {config['browser_type']}")
#     else:
#         print("❌ 配置加载失败")

if __name__ == "__main__":
    print(str(Path(__file__).parent))
    # test_config()
