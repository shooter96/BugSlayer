#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSH客户端函数模块

这个模块提供了SSH连接相关的函数，包括连接建立、命令执行、连接断开等功能。
所有函数都遵循参数类型注解和返回值类型注解的规范。
"""

import logging
import socket
import time
from typing import Optional, Tuple
import paramiko

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 设置日志级别
if logger.handlers:
    logger.handlers.clear()

# 创建 formatter（格式化器）
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s'
)

# --- 1. 创建 FileHandler：输出到文件 ---
file_handler = logging.FileHandler('../log/module_test.log', encoding='utf-8')
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

# --- 2. 创建 StreamHandler：输出到控制台 ---
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # 控制台只输出 INFO 及以上级别
console_handler.setFormatter(formatter)

# --- 将 handlers 添加到 logger ---
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def connect_ssh(ip: str, port: int, username: str, password: str, 
                max_retries: int = 3, retry_delay: float = 2.0) -> Tuple[bool, Optional[paramiko.SSHClient]]:
    """
    建立SSH连接，支持重试机制
    
    Args:
        ip: 服务器IP地址
        port: SSH端口
        username: 用户名
        password: 密码
        max_retries: 最大重试次数，默认为3
        retry_delay: 重试延迟时间（秒），默认为2.0
        
    Returns:
        Tuple[bool, Optional[paramiko.SSHClient]]: (连接是否成功, SSH客户端对象)
        
    Raises:
        paramiko.AuthenticationException: 认证失败异常
    """
    ssh_client = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"尝试连接 {ip}:{port} (尝试 {attempt + 1}/{max_retries})")
            
            # 创建SSH客户端
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 设置连接参数
            connect_kwargs = {
                'hostname': ip,
                'port': port,
                'username': username,
                'password': password,
                'timeout': 30,  # 连接超时时间
                'banner_timeout': 30,  # banner读取超时
                'auth_timeout': 30,  # 认证超时
                'look_for_keys': False,  # 不查找密钥文件
                'allow_agent': False  # 不使用SSH agent
            }
            
            # 建立连接
            ssh_client.connect(**connect_kwargs)
            
            # 验证连接
            if test_ssh_connection(ssh_client):
                logger.info(f"成功连接到 {ip}:{port}")
                return True, ssh_client
            else:
                logger.warning(f"连接测试失败 {ip}:{port}")
                ssh_client.close()
                ssh_client = None
                
        except paramiko.ssh_exception.SSHException as e:
            logger.error(f"SSH异常 (尝试 {attempt + 1}): {str(e)}")
            if "reading ssh protocol banner" in str(e).lower():
                logger.info("检测到SSH banner读取问题，尝试调整超时设置...")
                
        except paramiko.AuthenticationException as e:
            logger.error(f"认证失败 (尝试 {attempt + 1}): {str(e)}")
            if ssh_client:
                try:
                    ssh_client.close()
                except:
                    pass
            raise  # 认证失败不重试
            
        except socket.timeout as e:
            logger.error(f"连接超时 (尝试 {attempt + 1}): {str(e)}")
            
        except Exception as e:
            logger.error(f"连接失败 (尝试 {attempt + 1}): {type(e).__name__}: {str(e)}")
            
        if attempt < max_retries - 1:
            logger.info(f"等待 {retry_delay} 秒后重试...")
            time.sleep(retry_delay)
            retry_delay *= 1.5  # 指数退避
        
        if ssh_client:
            try:
                ssh_client.close()
            except:
                pass
            ssh_client = None
    
    logger.error(f"连接 {ip}:{port} 失败，已尝试 {max_retries} 次")
    return False, None


def test_ssh_connection(ssh_client: paramiko.SSHClient) -> bool:
    """
    测试SSH连接是否正常
    
    Args:
        ssh_client: SSH客户端对象
        
    Returns:
        bool: 连接是否正常
        
    Raises:
        Exception: 连接测试过程中的异常
    """
    try:
        if not ssh_client:
            return False
            
        # 执行一个简单的命令测试连接
        stdin, stdout, stderr = ssh_client.exec_command("echo 'test'")
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        
        return output == "test" and not error
        
    except Exception as e:
        logger.error(f"连接测试失败: {str(e)}")
        return False


def disconnect_ssh(ssh_client: paramiko.SSHClient, ip: str = "", port: int = 22) -> None:
    """
    断开SSH连接
    
    Args:
        ssh_client: SSH客户端对象
        ip: 服务器IP地址（用于日志记录）
        port: SSH端口（用于日志记录）
        
    Returns:
        None
        
    Raises:
        Exception: 断开连接过程中的异常
    """
    if ssh_client:
        try:
            ssh_client.close()
            if ip:
                logger.info(f"已断开与 {ip}:{port} 的连接")
            else:
                logger.info("已断开SSH连接")
        except Exception as e:
            logger.error(f"断开连接时出错: {str(e)}")


def execute_ssh_command(ssh_client: paramiko.SSHClient, command: str, 
                       timeout: int = 30) -> Tuple[str, str, Optional[str]]:
    """
    执行SSH命令并返回结果，增加超时控制
    
    Args:
        ssh_client: SSH客户端对象
        command: 要执行的命令
        timeout: 命令执行超时时间（秒），默认为30
        
    Returns:
        Tuple[str, str, Optional[str]]: (标准输出, 标准错误, 错误信息)
        错误信息为None表示执行成功
        
    Raises:
        socket.timeout: 命令执行超时
        Exception: 命令执行过程中的其他异常
    """
    if not ssh_client:
        return None, None, "未建立连接"
    
    try:
        logger.debug(f"执行命令: {command}")
        stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout)
        
        # 读取输出
        stdout_data = stdout.read().decode('utf-8')
        stderr_data = stderr.read().decode('utf-8')
        
        # 检查返回码
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            error_msg = f"命令执行失败 (exit code: {exit_status})"
            if stderr_data:
                error_msg += f": {stderr_data.strip()}"
            return stdout_data, stderr_data, error_msg
        
        return stdout_data, stderr_data, None
        
    except socket.timeout:
        return None, None, f"命令执行超时 (>{timeout}s)"
    except Exception as e:
        return None, None, f"执行命令出错: {str(e)}"

def transfer_file(client, local_path, remote_path):
    """
    通过SSH传输文件
    
    Args:
        client: SSH客户端对象
        local_path: 本地文件路径
        remote_path: 远程服务器目标路径
    
    Returns:
        bool: 传输是否成功
    """
    try:
        # 检查本地文件是否存在
        import os
        if not os.path.exists(local_path):
            logger.error(f"本地文件不存在: {local_path}")
            return False
            
        # 使用SFTP进行文件传输
        sftp = client.open_sftp()
        
        # 传输文件
        sftp.put(local_path, remote_path)
        
        # 关闭SFTP连接
        sftp.close()
        
        logger.info(f"文件传输成功: {local_path} -> {remote_path}")
        return True
        
    except Exception as e:
        logger.error(f"文件传输失败: {e}")
        return False
