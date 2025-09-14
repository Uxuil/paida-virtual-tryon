# 安全配置说明

## 🔐 环境变量配置

本项目使用环境变量来管理敏感信息，请按照以下步骤配置：

### 1. 复制环境变量模板
```bash
cp env.example .env
```

### 2. 配置必要的环境变量
编辑 `.env` 文件，填入你的实际配置：

```bash
# 阿里云DashScope API配置
DASHSCOPE_API_KEY=sk-your-actual-api-key-here

# 阿里云OSS配置
OSS_ACCESS_KEY_ID=your-oss-access-key-id
OSS_ACCESS_KEY_SECRET=your-oss-access-key-secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=your-bucket-name

# JWT配置
JWT_SECRET_KEY=your-super-secret-jwt-key

# Flask配置
FLASK_DEBUG=False
FLASK_ENV=production
```

### 3. 启动应用
```bash
# 后端
cd backend
python app.py

# 前端
cd frontend
python -m http.server 8080
```

## ⚠️ 安全注意事项

1. **永远不要将 `.env` 文件提交到Git仓库**
2. **定期轮换API密钥**
3. **使用强密码作为JWT密钥**
4. **在生产环境中使用HTTPS**
5. **限制API访问权限**

## 🛡️ 已实施的安全措施

- ✅ 移除了硬编码的API密钥
- ✅ 使用环境变量管理敏感信息
- ✅ 添加了.gitignore排除敏感文件
- ✅ 提供了环境变量模板文件
- ✅ 添加了安全配置文档

## 📝 部署检查清单

在部署到生产环境前，请确认：

- [ ] 所有敏感信息都通过环境变量配置
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 使用了强密码和安全的API密钥
- [ ] 配置了适当的CORS策略
- [ ] 启用了HTTPS
- [ ] 设置了适当的文件上传限制