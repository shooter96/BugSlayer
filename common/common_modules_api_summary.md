# Common Modules API Summary

## 概述
本文档总结了 `common` 目录下四个核心模块的函数接口，包括登录模块、JSON配置加载模块、导航模块和SSH客户端模块。

## 1. 登录模块 (login.py)

### 1.1 setup_browser
**功能**: 设置浏览器环境，支持多种浏览器类型和客户端证书认证

**参数**:
- `converted_crt_path` (str): 客户端证书文件路径（CRT格式）
- `converted_key_path` (str): 客户端私钥文件路径（KEY格式）  
- `config` (dict): 配置信息字典，包含headless、slow_mo、url等配置
- `browser_type` (str, optional): 浏览器类型，支持 'chromium', 'firefox', 'webkit', 'msedge'，默认为None（使用config中的配置）

**返回值**: `tuple` - (playwright, browser, context, page)

**说明**: 创建支持HTTPS双向认证的浏览器环境，设置视口大小为1920x1080，启用追踪功能

---

### 1.2 access_https_page
**功能**: 访问HTTPS页面并处理证书警告

**参数**:
- `page` (Page): Playwright页面对象
- `config` (dict): 配置信息字典，包含默认URL
- `url` (str, optional): 要访问的具体URL地址，未提供则使用config中的url

**返回值**: `bool` - 页面访问结果（True: 成功或超时但继续执行，False: 访问失败）

**异常处理**: 捕获页面加载超时异常，记录警告日志后继续执行

---

### 1.3 create_https_page
**功能**: 通过浏览器对象创建HTTPS页面（用于已有浏览器状态下创建新页面）

**参数**:
- `browser`: Playwright浏览器对象
- `converted_crt_path` (str): 客户端证书文件路径（CRT格式）
- `converted_key_path` (str): 客户端私钥文件路径（KEY格式）
- `config` (dict): 配置信息字典
- `url` (str, optional): 要访问的具体URL地址

**返回值**: `Page/None` - 新创建的页面对象或None（创建失败）

**说明**: 区别于access_https_page，用于在已有浏览器状态下创建支持HTTPS认证的新页面

---

### 1.4 login_to_system
**功能**: 通用登录系统函数，自动识别登录表单元素

**参数**:
- `page` (Page): Playwright页面对象
- `username` (str, optional): 用户名
- `password` (str, optional): 密码

**返回值**: `bool` - 登录操作结果

**实现特点**:
- 使用多种CSS选择器策略定位元素（type、name、id、placeholder等属性）
- 用户名和密码输入框支持多种选择器组合
- 登录按钮支持submit类型和文本内容匹配
- 每个元素查找超时时间为3秒
- 密码在日志中以星号显示保证安全性

---

### 1.5 login_to_80_system
**功能**: 专门针对80端口系统的登录流程

**参数**:
- `page` (Page): Playwright页面对象
- `config` (dict): 配置信息字典，包含默认用户名密码
- `username` (str, optional): 用户名，未提供使用config中的配置
- `password` (str, optional): 密码，未提供使用config中的配置

**返回值**: `bool` - 登录操作结果

**特点**: 登录按钮基于li元素而非标准button/input元素，专门针对80端口系统的特殊登录界面

---

### 1.6 log_out
**功能**: 退出443/442端口系统登录

**参数**:
- `page`: Playwright页面对象
- `port` (str): 端口号，支持"443"和"442"，默认为"443"

**返回值**: `bool` - 退出操作结果

**注意**: 使用动态ID选择器（#ext-gen90、#ext-gen93），可能存在兼容性问题

---

### 1.7 cleanup
**功能**: 清理Playwright浏览器资源

**参数**:
- `playwright`: Playwright对象
- `browser`: 浏览器对象
- `context`: 浏览器上下文对象

**返回值**: None

**特点**: 幂等操作设计，所有异常都被捕获并记录，不会抛出异常中断程序

---

## 2. JSON配置加载模块 (json_load.py)

### 2.1 load_json_config
**功能**: 加载JSON配置文件

**参数**:
- `config_file` (str): JSON配置文件的路径（相对路径或绝对路径）

**返回值**: `dict` - 解析后的配置数据（成功: 配置信息字典，失败: 空字典{}）

**实现特点**:
- 使用UTF-8编码读取文件，支持中文路径和内容
- 使用json.load()直接解析文件对象，效率高
- 异常捕获使用通用Exception，处理所有可能的错误
- 加载失败时返回空字典，避免程序崩溃

---

## 3. 导航模块 (navigate.py)

### 3.1 navigate_to_menu
**功能**: 通用导航函数 - 导航到指定菜单模块

**参数**:
- `page` (Page): Playwright页面对象
- `menu_name` (str): 菜单名称
- `selectors` (list, optional): 自定义CSS选择器列表，未提供使用默认选择器

**返回值**: `bool` - 导航操作结果

**默认选择器策略**:
- `text={menu_name}`
- `a:has-text('{menu_name}')`
- `span:has-text('{menu_name}')`

**特点**: 智能匹配菜单元素，适配不同前端框架，异常被捕获并继续尝试下一个选择器

---

### 3.2 check_service_exists
**功能**: 检查服务是否存在于树形导航结构中

**参数**:
- `page` (Page): Playwright页面对象
- `service_name` (str): 要查找的服务名称

**返回值**: `bool` - 服务存在性检查结果

**树形容器选择器**:
- `#ktree`
- `.x-tree-root-ct`
- `.x-tree-root-node`

**服务元素选择器**:
- `span:text-is('{service_name}')`
- `a span:text-is('{service_name}')`
- `.x-tree-node-anchor span:text-is('{service_name}')`
- `[ext:tree-node-id*='{service_name}']`

---

### 3.3 navigate_to_business_by_name
**功能**: 根据业务名称导航到指定业务页面

**参数**:
- `page` (Page): Playwright页面对象
- `service_name` (str): 要导航到的业务名称

**返回值**: `bool` - 导航操作结果

**流程**:
1. 首先调用check_service_exists检查服务存在性
2. 在树形结构中查找并点击目标业务
3. 等待页面加载完成（networkidle状态，10秒超时）

**特点**: 依赖check_service_exists的结果，提供完整的导航流程和错误处理

---

## 4. SSH客户端模块 (ssh_client.py)

### 4.1 connect_ssh
**功能**: 建立SSH连接，支持重试机制

**参数**:
- `ip` (str): 服务器IP地址
- `port` (int): SSH端口
- `username` (str): 用户名
- `password` (str): 密码
- `max_retries` (int): 最大重试次数，默认为3
- `retry_delay` (float): 重试延迟时间（秒），默认为2.0

**返回值**: `Tuple[bool, Optional[paramiko.SSHClient]]` - (连接是否成功, SSH客户端对象)

**异常处理**:
- `paramiko.AuthenticationException`: 认证失败异常（不重试）
- `paramiko.ssh_exception.SSHException`: SSH异常
- `socket.timeout`: 连接超时
- 其他异常：通用异常处理

**特点**:
- 支持指数退避重试策略（retry_delay *= 1.5）
- 连接参数包含完整的超时设置（30秒）
- 禁用密钥文件查找和SSH agent
- 连接成功后执行测试验证

---

### 4.2 test_ssh_connection
**功能**: 测试SSH连接是否正常

**参数**:
- `ssh_client` (paramiko.SSHClient): SSH客户端对象

**返回值**: `bool` - 连接是否正常

**测试方法**: 执行简单命令`echo 'test'`，检查输出是否为"test"且无误信息

---

### 4.3 disconnect_ssh
**功能**: 断开SSH连接

**参数**:
- `ssh_client` (paramiko.SSHClient): SSH客户端对象
- `ip` (str, optional): 服务器IP地址（用于日志记录）
- `port` (int, optional): SSH端口（用于日志记录）

**返回值**: None

**特点**: 安全的连接断开，异常内部处理，提供详细的日志记录

---

### 4.4 execute_ssh_command
**功能**: 执行SSH命令并返回结果，增加超时控制

**参数**:
- `ssh_client` (paramiko.SSHClient): SSH客户端对象
- `command` (str): 要执行的命令
- `timeout` (int): 命令执行超时时间（秒），默认为30

**返回值**: `Tuple[str, str, Optional[str]]` - (标准输出, 标准错误, 错误信息)

**错误信息说明**:
- None: 执行成功
- "未建立连接": SSH客户端对象为空
- "命令执行超时 (>{timeout}s)": 命令执行超时
- "命令执行失败 (exit code: {code}): {stderr}": 命令返回非零退出码
- "执行命令出错: {error}": 其他执行异常

**特点**:
- 检查命令返回码，非零状态视为失败
- 完整的异常处理，包括超时和通用异常
- 详细的错误信息返回，便于问题定位

---

## 通用特性

### 日志配置
所有模块都采用统一的日志配置：
- **日志格式**: `'%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s'`
- **文件处理器**: 输出到 `../log/module_test.log`，级别为WARNING
- **控制台处理器**: 输出到控制台，级别为INFO
- **编码**: UTF-8，支持中文日志内容

### 错误处理原则
1. **异常安全**: 所有函数都进行异常捕获，不会抛出未处理异常
2. **详细日志**: 记录操作成功/失败状态，包含具体的错误信息
3. **返回值明确**: 成功/失败状态通过布尔值或特定数据结构明确返回
4. **资源清理**: 确保资源正确释放，避免内存泄漏

### 代码规范
- 所有函数都包含详细的docstring文档
- 参数和返回值都进行类型注解
- 遵循Python代码规范，使用有意义的变量名
- 统一的日志记录格式和级别规范