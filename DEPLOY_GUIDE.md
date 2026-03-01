# 狐狸学社网站部署指南

## 概述

本指南将帮助你把狐狸学社网站从 "上线了" 平台迁移到自主托管的腾讯云 COS。

## 准备工作

### 1. GitHub 账号
- 已注册: xuminhu
- 访问: https://github.com/xuminhu

### 2. 腾讯云 COS
- 存储桶: foxsociety-website-1313164395
- 地域: ap-shanghai
- 已获取 SecretId 和 SecretKey

### 3. 域名
- 当前: www.foxsociety.com.cn（在"上线了"平台）
- 等待邮件回复获取 DNS 管理权限

---

## 部署步骤

### 第一步：创建 GitHub 仓库

1. 登录 GitHub (xuminhu)
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - Repository name: `foxsociety-website`
   - Description: 狐狸学社官方网站
   - Public（公开）
   - 勾选 "Add a README file"
4. 点击 "Create repository"

### 第二步：上传代码

在本地终端执行：

```bash
# 进入项目目录
cd foxsociety-website

# 初始化 git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Fox Society website"

# 关联远程仓库
git remote add origin https://github.com/xuminhu/foxsociety-website.git

# 推送
git push -u origin main
```

### 第三步：配置 GitHub Secrets

1. 进入 GitHub 仓库页面
2. 点击 "Settings" → "Secrets and variables" → "Actions"
3. 点击 "New repository secret"
4. 添加两个 secret：
   - Name: `TENCENT_SECRET_ID`
     Value: [你的 SecretId]
   - Name: `TENCENT_SECRET_KEY`
     Value: [你的 SecretKey]

### 第四步：配置腾讯云 COS

1. 登录腾讯云控制台 → 对象存储 COS
2. 进入存储桶 `foxsociety-website-1313164395`
3. 点击 "基础配置" → "静态网站"
4. 开启静态网站，设置：
   - 默认首页: `index.html`
   - 默认错误页: `404.html`
5. 保存

### 第五步：开启全球加速

1. 在存储桶页面，点击 "域名传输管理" → "自定义 CDN 加速域名"
2. 添加域名: `www.foxsociety.com.cn`
3. 开启 HTTPS（申请免费 SSL 证书）
4. 开启全球加速

### 第六步：配置域名 DNS

等待 "上线了" 邮件回复后：

**方案 A：获得域名转移码**
1. 在腾讯云控制台 → 域名注册 → 域名转入
2. 使用转移码转入域名
3. 修改 DNS 服务器为腾讯云默认

**方案 B：仅修改 DNS 解析**
1. 在 "上线了" 后台找到 DNS 管理
2. 添加 CNAME 记录：
   - 主机记录: www
   - 记录值: [腾讯云 CDN 域名]
3. 或修改 NS 服务器为腾讯云 DNS

### 第七步：验证部署

1. 在 GitHub 仓库点击 "Actions" 标签
2. 查看部署状态（绿色勾表示成功）
3. 访问 `https://www.foxsociety.com.cn` 查看网站

---

## 后续内容更新

### 添加新案例

1. 在 `content/cases/` 创建新文件
2. 参考现有案例格式填写 front matter
3. git add → git commit → git push
4. 自动部署（约 2 分钟）

### 修改现有内容

直接修改对应 Markdown 文件，推送后自动部署。

---

## 常见问题

### Q: 部署失败怎么办？
A: 查看 GitHub Actions 日志，检查：
- Secrets 配置是否正确
- 存储桶名称和地域是否正确
- Hugo 构建是否有错误

### Q: 如何预览修改效果？
A: 本地运行 `hugo server -D`，访问 http://localhost:1313

### Q: 域名转移失败怎么办？
A: 先使用方案 B（修改 DNS 解析），网站可立即上线，再慢慢协商域名转移。

### Q: 如何备份网站？
A: GitHub 仓库本身就是完整备份，随时可克隆恢复。

---

## 联系支持

如有问题，请联系：
- 微信: FoxSociety
- 邮箱: contact@foxsociety.com.cn
