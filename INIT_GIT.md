# Git 初始化步骤

## 第一步：重启终端
安装 Git 后，**必须重启终端**（关闭并重新打开 PowerShell）才能使用 Git 命令。

## 第二步：验证 Git 安装
重启终端后，运行：
```bash
git --version
```
如果显示版本号（如 `git version 2.x.x`），说明安装成功。

## 第三步：初始化 Git 仓库

在项目目录中执行以下命令：

```bash
# 1. 确保在项目目录
cd C:\Users\User\Downloads\oic

# 2. 初始化 Git 仓库
git init

# 3. 配置 Git 用户信息（首次使用需要）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 4. 添加所有文件
git add .

# 5. 创建首次提交
git commit -m "Initial commit: OIC Education application"
```

## 第四步：连接到 GitHub

1. **在 GitHub 上创建新仓库**
   - 访问 https://github.com
   - 点击右上角 "+" → "New repository"
   - 输入仓库名称（例如：`oic-education`）
   - 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"
   - 点击 "Create repository"

2. **连接本地仓库到 GitHub**
```bash
# 替换 YOUR_USERNAME 和 YOUR_REPO_NAME 为你的实际值
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 例如：
# git remote add origin https://github.com/johnsmith/oic-education.git
```

## 第五步：推送到 GitHub

```bash
# 设置主分支名称
git branch -M main

# 推送到 GitHub（首次推送）
git push -u origin main
```

**注意**：首次推送时，GitHub 会要求身份验证。你需要使用 **Personal Access Token**（不是密码）。

### 如何创建 Personal Access Token：
1. 登录 GitHub
2. 点击右上角头像 → Settings
3. 左侧菜单：Developer settings
4. Personal access tokens → Tokens (classic)
5. Generate new token (classic)
6. 选择权限：勾选 `repo`（完整仓库访问权限）
7. 生成并复制 Token（只显示一次，请保存好）
8. 推送时，用户名输入你的 GitHub 用户名，密码输入 Token

## 快速检查清单

- [ ] Git 已安装并重启了终端
- [ ] `git --version` 可以运行
- [ ] 已配置 Git 用户信息
- [ ] 已在 GitHub 创建仓库
- [ ] 已创建 Personal Access Token
- [ ] 已执行 `git init`
- [ ] 已执行 `git add .`
- [ ] 已执行 `git commit`
- [ ] 已连接远程仓库
- [ ] 已成功推送

## 如果遇到问题

1. **Git 命令无法识别**
   - 确保已重启终端
   - 检查 Git 安装路径是否在系统 PATH 中

2. **推送时认证失败**
   - 使用 Personal Access Token 而不是密码
   - 确保 Token 有 `repo` 权限

3. **查看帮助**
   - `git help` - 查看 Git 帮助
   - `git status` - 查看当前状态
   - `git log` - 查看提交历史

