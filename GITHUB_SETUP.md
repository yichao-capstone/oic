# 如何将项目推送到 GitHub

## 前提条件

1. **安装 Git**
   - 下载并安装 Git: https://git-scm.com/download/win
   - 安装完成后，重启终端

2. **创建 GitHub 账户**
   - 如果没有账户，访问 https://github.com 注册

3. **在 GitHub 上创建新仓库**
   - 登录 GitHub
   - 点击右上角的 "+" → "New repository"
   - 输入仓库名称（例如：oic-education）
   - 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"
   - 点击 "Create repository"

## 推送步骤

### 1. 初始化 Git 仓库

```bash
# 在项目目录中打开终端（PowerShell 或 CMD）
cd C:\Users\User\Downloads\oic

# 初始化 Git 仓库
git init
```

### 2. 添加所有文件

```bash
# 添加所有文件到暂存区
git add .

# 或者只添加特定文件
# git add *.py requirements.txt .gitignore
```

### 3. 创建首次提交

```bash
# 创建提交
git commit -m "Initial commit: OIC Education application"
```

### 4. 连接到 GitHub 仓库

```bash
# 将本地仓库连接到 GitHub（替换 YOUR_USERNAME 和 YOUR_REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 例如：
# git remote add origin https://github.com/yourusername/oic-education.git
```

### 5. 推送到 GitHub

```bash
# 推送到 GitHub（首次推送）
git branch -M main
git push -u origin main
```

## 后续更新

当代码有更改时，使用以下命令更新：

```bash
# 1. 查看更改状态
git status

# 2. 添加更改的文件
git add .

# 3. 提交更改
git commit -m "描述你的更改"

# 4. 推送到 GitHub
git push
```

## 注意事项

1. **`.streamlit/secrets.toml` 文件**
   - 这个文件包含敏感信息，已经在 `.gitignore` 中被排除
   - **不要**将其推送到 GitHub

2. **首次推送可能需要身份验证**
   - GitHub 现在使用 Personal Access Token 而不是密码
   - 创建 Token: GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - 权限选择：`repo`（完整仓库访问权限）

3. **如果遇到错误**
   - 确保 Git 已正确安装：`git --version`
   - 检查远程仓库地址：`git remote -v`
   - 查看详细错误信息进行排查

## 快速命令参考

```bash
# 初始化仓库
git init

# 添加文件
git add .

# 提交
git commit -m "提交信息"

# 添加远程仓库
git remote add origin https://github.com/USERNAME/REPO.git

# 推送
git push -u origin main

# 查看状态
git status

# 查看提交历史
git log
```

