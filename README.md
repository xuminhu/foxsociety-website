# 狐狸学社网站 Fox Society Website

基于 Hugo 构建的静态网站，部署在腾讯云 COS。

## 项目结构

```
.
├── archetypes/          # 内容模板
├── assets/              # 资源文件（CSS/JS/图片）
├── content/             # 网站内容
│   ├── cases/          # 案例
│   ├── services/       # 服务
│   ├── about.md        # 关于我们
│   ├── contact.md      # 联系我们
│   └── en/             # 英文内容
├── layouts/             # HTML 模板
│   ├── _default/       # 默认模板
│   └── index.html      # 首页模板
├── static/              # 静态资源
├── hugo.toml           # Hugo 配置
└── .github/workflows/   # GitHub Actions 自动部署
```

## 本地开发

### 安装 Hugo

```bash
# macOS
brew install hugo

# Windows
choco install hugo-extended

# Linux
sudo apt install hugo
```

### 本地预览

```bash
# 克隆仓库
git clone https://github.com/xuminhu/foxsociety-website.git
cd foxsociety-website

# 启动开发服务器
hugo server -D

# 访问 http://localhost:1313
```

### 构建

```bash
hugo --minify
```

构建后的文件在 `public/` 目录。

## 内容管理

### 添加新案例

在 `content/cases/` 创建新的 Markdown 文件：

```markdown
---
title: "学生姓名 - 专业方向"
student_name: "城市姓名"
direction: "专业"
schools: ["学校1", "学校2"]
sat: "1500"
toefl: "110"
date: 2024-01-01
---

案例内容...
```

### 添加英文内容

在 `content/en/cases/` 创建对应英文版本。

## 自动部署

推送到 `main` 分支自动触发部署到腾讯云 COS。

### 配置 Secrets

在 GitHub 仓库设置中添加：

- `TENCENT_SECRET_ID`: 腾讯云 SecretId
- `TENCENT_SECRET_KEY`: 腾讯云 SecretKey

## 域名配置

1. 在腾讯云 COS 开启静态网站托管
2. 配置自定义域名 `www.foxsociety.com.cn`
3. 开启 HTTPS 和全球加速

## 技术栈

- [Hugo](https://gohugo.io/) - 静态网站生成器
- [腾讯云 COS](https://cloud.tencent.com/product/cos) - 对象存储
- [GitHub Actions](https://github.com/features/actions) - 自动部署

## 维护

- 每半年更新案例内容
- 定期检查链接有效性
- 监控网站访问速度
- 
Website deployed to Tencent COS.

---

**狐狸学社 Fox Society**
专注于挖掘学生闪光点，帮助每位学生成为具有国际视野的青年学者
