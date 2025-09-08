# Quality Control Application - 完整部署指南

## 🚀 部署选项

### 1. 简单启动（开发测试）
```bash
python deploy_waitress_production.py
```

### 2. 使用启动脚本
```bash
python start_server.py
```

### 3. Windows批处理文件
```bash
run_waitress.bat
```

### 4. Windows服务安装（生产环境推荐）

#### 安装依赖
```bash
pip install pywin32
```

#### 安装服务（需要管理员权限）
```bash
python install_waitress_service.py install
```

#### 启动服务
```bash
python install_waitress_service.py start
```

#### 停止服务
```bash
python install_waitress_service.py stop
```

#### 卸载服务
```bash
python install_waitress_service.py remove
```

#### 调试模式
```bash
python install_waitress_service.py debug
```

## ⚙️ 配置说明

### 端口和主机配置
默认配置：
- **主机**: 0.0.0.0（监听所有网络接口）
- **端口**: 8000

修改配置：编辑 `deploy_waitress_production.py` 文件中的 `serve()` 函数参数。

### 线程配置
默认使用4个线程，可根据服务器性能调整。

## 🔧 生产环境设置

### 1. 应用生产环境配置
将 `production_settings.py` 中的设置复制到 `quality_control/settings.py` 或直接使用环境变量：

```bash
# 设置环境变量
set SECRET_KEY=your-secure-production-key
set DEBUG=False
```

### 2. 收集静态文件
```bash
python manage.py collectstatic --noinput
```

### 3. 数据库迁移
```bash
python manage.py migrate
```

## 📊 监控和维护

### 检查服务状态
```bash
sc query QualityControlWaitress
```

### 查看日志
- 应用日志: `logs/django.log`
- Windows事件日志: 查看"Quality Control Waitress Server"服务日志

### 重启服务
```bash
python install_waitress_service.py stop
python install_waitress_service.py start
```

## 🛡️ 安全建议

### 1. 修改默认密钥
```python
# 在 production_settings.py 中修改
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secure-production-key')
```

### 2. 配置防火墙
- 只允许必要端口（8000）的访问
- 限制访问IP范围

### 3. 启用HTTPS（推荐）
使用反向代理（如Nginx）配置SSL证书

### 4. 定期备份
- 数据库备份
- 应用代码备份
- 日志文件备份

## 🚨 故障排除

### 端口占用错误
```bash
# 查看占用8000端口的进程
netstat -ano | findstr :8000

# 终止进程
taskkill /f /pid <PID>
```

### 服务启动失败
1. 检查事件查看器中的错误信息
2. 确保所有依赖已安装
3. 验证数据库连接

### 静态文件无法访问
```bash
# 重新收集静态文件
python manage.py collectstatic --noinput

# 检查静态文件目录权限
```

### 数据库连接问题
确保MySQL服务正在运行：
```bash
# 启动MySQL服务
net start mysql
```

## 📋 系统要求

### 最低配置
- Python 3.8+
- MySQL 5.7+
- 2GB RAM
- 10GB硬盘空间

### 推荐配置
- Python 3.10+
- MySQL 8.0+
- 4GB RAM
- 20GB硬盘空间

## 🔄 更新流程

### 1. 停止服务
```bash
python install_waitress_service.py stop
```

### 2. 备份数据
```bash
# 备份数据库
mysqldump -u root -p quality_control > backup_$(date +%Y%m%d).sql
```

### 3. 更新代码
```bash
git pull origin main
```

### 4. 更新依赖
```bash
pip install -r requirements.txt
```

### 5. 数据库迁移
```bash
python manage.py migrate
```

### 6. 重启服务
```bash
python install_waitress_service.py start
```

## 📞 技术支持

### 日志位置
- 应用日志: `logs/django.log`
- 服务日志: Windows事件查看器 → 应用程序和服务日志

### 常见问题
1. **服务无法启动**: 检查Python路径和依赖
2. **数据库连接失败**: 验证MySQL服务状态和连接参数
3. **静态文件404**: 运行collectstatic命令

### 紧急恢复
```bash
# 强制停止所有Python进程
taskkill /f /im python.exe

# 重新启动服务
python install_waitress_service.py start
```

---

**最后更新**: 2025-09-07  
**版本**: 1.0.0
