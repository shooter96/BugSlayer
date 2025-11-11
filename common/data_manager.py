import json
import csv
import yaml
import openpyxl
from pathlib import Path
from typing import List, Dict, Any
from common.logger import get_logger

logger = get_logger(__name__)

class DataManager:
    """测试数据管理器"""
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """
        加载JSON文件
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            Dict[str, Any]: JSON数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file) #直接解析文件对象
                logger.info(f"✅ 成功加载JSON文件: {file_path}")
                return data
        except Exception as e:
            logger.error(f"❌ 加载JSON文件失败: {file_path}, 错误: {e}")
            return {}
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: str):
        """
        保存JSON文件
        
        Args:
            data: 要保存的数据
            file_path: 保存路径
        """
        try:
            # 确保目录存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                logger.info(f"成功保存JSON文件: {file_path}")
        except Exception as e:
            logger.error(f"保存JSON文件失败: {file_path}, 错误: {e}")
    
    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        """
        加载YAML文件
        
        Args:
            file_path: YAML文件路径
            
        Returns:
            Dict[str, Any]: YAML数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                logger.info(f"成功加载YAML文件: {file_path}")
                return data
        except Exception as e:
            logger.error(f"加载YAML文件失败: {file_path}, 错误: {e}")
            return {}
    
    @staticmethod
    def load_csv(file_path: str) -> List[Dict[str, Any]]:
        """
        加载CSV文件
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            List[Dict[str, Any]]: CSV数据列表
        """
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
                logger.info(f"成功加载CSV文件: {file_path}, 共 {len(data)} 行数据")
                return data
        except Exception as e:
            logger.error(f"加载CSV文件失败: {file_path}, 错误: {e}")
            return []
    
    @staticmethod
    def load_excel(file_path: str, sheet_name: str = None) -> List[Dict[str, Any]]:
        """
        加载Excel文件
        
        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称，为None时使用第一个工作表
            
        Returns:
            List[Dict[str, Any]]: Excel数据列表
        """
        try:
            workbook = openpyxl.load_workbook(file_path)
            
            if sheet_name:
                worksheet = workbook[sheet_name]
            else:
                worksheet = workbook.active
            
            data = []
            headers = []
            
            # 获取表头
            for cell in worksheet[1]:
                headers.append(cell.value)
            
            # 获取数据行
            for row in worksheet.iter_rows(min_row=2, values_only=True):
                row_data = {}
                for i, value in enumerate(row):
                    if i < len(headers):
                        row_data[headers[i]] = value
                data.append(row_data)
            
            logger.info(f"成功加载Excel文件: {file_path}, 工作表: {sheet_name or 'default'}, 共 {len(data)} 行数据")
            return data
            
        except Exception as e:
            logger.error(f"加载Excel文件失败: {file_path}, 错误: {e}")
            return []
    
    @staticmethod
    def get_test_data(data_file: str, test_case: str = None) -> List[Dict[str, Any]]:
        """
        获取测试数据
        
        Args:
            data_file: 数据文件路径
            test_case: 测试用例名称，用于过滤数据
            
        Returns:
            List[Dict[str, Any]]: 测试数据列表
        """
        file_path = Path(f"test_data/{data_file}")
        
        if not file_path.exists():
            logger.error(f"测试数据文件不存在: {file_path}")
            return []
        
        # 根据文件扩展名选择加载方法
        suffix = file_path.suffix.lower()
        
        if suffix == '.json':
            data = DataManager.load_json(str(file_path))
            if test_case and test_case in data:
                return data[test_case] if isinstance(data[test_case], list) else [data[test_case]]
            return [data] if isinstance(data, dict) else data
            
        elif suffix in ['.yaml', '.yml']:
            data = DataManager.load_yaml(str(file_path))
            if test_case and test_case in data:
                return data[test_case] if isinstance(data[test_case], list) else [data[test_case]]
            return [data] if isinstance(data, dict) else data
            
        elif suffix == '.csv':
            data = DataManager.load_csv(str(file_path))
            if test_case:
                # 过滤包含指定测试用例名称的数据
                filtered_data = [row for row in data if test_case in str(row.get('test_case', ''))]
                return filtered_data if filtered_data else data
            return data
            
        elif suffix in ['.xlsx', '.xls']:
            data = DataManager.load_excel(str(file_path))
            if test_case:
                # 过滤包含指定测试用例名称的数据
                filtered_data = [row for row in data if test_case in str(row.get('test_case', ''))]
                return filtered_data if filtered_data else data
            return data
            
        else:
            logger.error(f"不支持的文件格式: {suffix}")
            return []

class TestDataProvider:
    """测试数据提供器"""
    
    def __init__(self, base_path: str = "test_data"):
        """
        初始化测试数据提供器
        
        Args:
            base_path: 测试数据根目录
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def get_login_data(self) -> List[Dict[str, Any]]:
        """获取登录测试数据"""
        return DataManager.get_test_data("login_data.json")
    
    def get_user_data(self) -> List[Dict[str, Any]]:
        """获取用户测试数据"""
        return DataManager.get_test_data("user_data.yaml")
    
    def get_product_data(self) -> List[Dict[str, Any]]:
        """获取产品测试数据"""
        return DataManager.get_test_data("product_data.csv") 