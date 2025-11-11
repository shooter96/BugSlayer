import logging
from datetime import datetime
from pathlib import Path

def get_logger(name: str = __name__) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    log_file = log_dir / f"test_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

class TestLogger:
    """测试日志类"""
    
    def __init__(self, test_name: str):
        self.logger = get_logger(test_name)
        self.test_name = test_name
    
    def info(self, message: str):
        """记录信息日志"""
        self.logger.info(f"[{self.test_name}] {message}")
    
    def error(self, message: str):
        """记录错误日志"""
        self.logger.error(f"[{self.test_name}] {message}")
    
    def warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(f"[{self.test_name}] {message}")
    
    def debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(f"[{self.test_name}] {message}")
    
    def step(self, step_name: str):
        """记录测试步骤"""
        self.logger.info(f"[{self.test_name}] 执行步骤: {step_name}") 