# 寿光相亲网 - 婚恋交友平台

## 项目简介

本项目是一个基于 **uni-app（前端）** + **Django REST Framework（后端）** 的婚恋交友平台，主要服务于寿光本地用户的相亲交友需求。项目包含会员信息展示、幸福案例展示、用户数据采集等功能，并集成了 Django Admin 一键采集管理后台。

## 项目结构

```
matchmaking/
├── uni-app/                          # 前端项目（uni-app 跨平台应用）
│   ├── pages/                        # 页面文件
│   │   ├── index/index.vue           # 首页（TabBar 首页）
│   │   ├── home/home.vue             # 首页（TabBar 首页）
│   │   ├── xingFuAnLi/               # "我们脱单了" 幸福案例页面
│   │   ├── latest_updates/           # 动态页面
│   │   └── userDetail/               # 用户详情页面
│   ├── api/apis.js                   # API 接口封装
│   ├── utils/request.js              # 网络请求封装（基于 Promise）
│   ├── utils/common.js               # 公共工具函数
│   ├── utils/system.js               # 系统工具函数
│   ├── static/                       # 静态资源（图片、图标等）
│   ├── pages.json                    # 页面路由与 TabBar 配置
│   ├── manifest.json                 # uni-app 项目配置
│   └── uni_modules/                  # uni-app 插件模块
│       ├── uni-icons/                # 图标组件
│       ├── uni-pagination/           # 分页组件
│       └── uni-scss/                 # SCSS 样式工具
│
├── xiangqin-backend/                 # 后端项目（Django REST Framework）
│   ├── xiangqin/                     # Django 项目主配置
│   │   ├── settings.py               # 项目配置（数据库、跨域、DRF 等）
│   │   ├── urls.py                   # 主路由配置
│   │   └── wsgi.py / asgi.py         # WSGI/ASGI 部署入口
│   ├── apps/                         # Django 应用
│   │   ├── users/                    # 用户模块
│   │   │   ├── models.py             # 用户模型（Users、UsersProfile、UserProfilePhoto）
│   │   │   ├── views.py              # 用户列表、用户采集接口
│   │   │   ├── serializers.py        # 序列化器
│   │   │   ├── filters.py            # 过滤器
│   │   │   ├── admin.py              # Admin 后台配置（含采集管理快捷入口）
│   │   │   ├── admin_views.py        # Admin 一键采集管理视图
│   │   │   └── urls.py               # 路由
│   │   ├── tuodan/                   # 脱单/幸福案例模块
│   │   │   ├── models.py             # 幸福案例模型（XingFuAnLi、Activity、Images）
│   │   │   ├── views.py              # 案例列表、案例采集接口
│   │   │   ├── serializers.py        # 序列化器
│   │   │   └── urls.py               # 路由
│   │   └── quickstart/               # 快速入门示例应用
│   ├── crawl_data/                   # 数据采集模块
│   │   ├── getUsers.py               # 采集用户列表数据
│   │   ├── getObjectProfile.py       # 采集用户详细信息
│   │   ├── getAnli.py                # 采集幸福案例数据
│   │   ├── getMemberPage.py          # 采集会员页面
│   │   ├── getHeaders.py             # 请求头生成
│   │   ├── hashtoken.py              # hashtoken 生成
│   │   ├── crawl_menutype2.py        # 采集推荐会员（menutype=2/3，支持 lasttime 翻页）
│   │   └── crawl_profiles.py         # 批量采集用户详情和相册
│   ├── utils/                        # 工具模块
│   │   ├── CustomPagination.py       # 自定义分页器
│   │   ├── CustomResponse.py         # 自定义响应格式
│   │   └── tools.py                  # 工具函数（远程图片下载等）
│   ├── comm/db.py                    # 数据库公共基类
│   ├── media/                        # 媒体文件存储目录
│   ├── templates/                    # HTML 模板
│   │   └── admin/
│   │       └── crawl_dashboard.html  # Admin 采集管理页面模板
│   ├── manage.py                     # Django 管理脚本
│   └── requirements.txt              # Python 依赖清单
│
├── 接口文档.md                       # 接口文档（含原网站 API 分析）
├── CHANGELOG.md                      # 项目更新日志
└── README.md                         # 本文件
```

## 技术栈

### 前端
- **uni-app**：基于 Vue.js 的跨平台应用框架，可编译到 iOS、Android、H5 及各小程序平台
- **Vue.js**：前端 MVVM 框架
- **uni-ui 组件库**：uni-icons、uni-pagination、uni-scss 等

### 后端
- **Python 3.x + Django 4.2**：Web 框架
- **Django REST Framework**：RESTful API 构建
- **SQLite**：数据库（开发环境）
- **django-filter**：数据过滤支持
- **django-cors-headers**：跨域支持

### 数据采集
- **Requests**：HTTP 请求库，用于从目标网站（sgjhw.com）采集数据
- 支持采集：用户列表、用户详情、幸福案例、相亲活动等数据
- 支持 `lasttime` 参数翻页采集更早的会员数据

## 功能特性

### 前端功能
1. **首页**：展示 Banner、推荐会员等信息
2. **会员列表**：浏览相亲会员信息，支持按性别、城市搜索过滤
3. **幸福案例**：展示成功脱单案例（"我们脱单了"），支持分页
4. **动态页面**：展示最新会员动态
5. **用户详情**：查看会员详细资料和相册
6. **TabBar 导航**：底部导航栏切换页面

### 后端功能
1. **会员管理**：会员信息的增删改查，支持按昵称、城市等字段过滤
2. **幸福案例管理**：成功案例的展示与管理，支持分页
3. **相亲活动管理**：相亲活动展示与管理
4. **数据采集**：从寿光相亲网（sgjhw.com）自动采集会员数据、用户详情、幸福案例和相亲活动
5. **图片管理**：自动下载并存储远程头像和案例图片
6. **API 文档**：集成 coreapi 自动生成接口文档

### Admin 一键采集管理（⭐ 新增）
- **访问地址**：`http://localhost:8000/admin/crawl/`（需登录 Django Admin）
- **一键采集全部**：依次采集所有数据
- **推荐会员采集**：支持 menutype=2/3 分类采集
- **可能喜欢的人**：采集"可能喜欢的人"推荐会员
- **用户详情和相册**：批量采集缺少详细资料的会员
- **幸福案例采集**：采集幸福案例
- **相亲活动采集**：采集相亲活动
- **实时日志**：采集过程实时显示日志输出
- **进度显示**：采集状态和进度条实时更新
- **数据统计**：顶部显示会员总数、有资料数、照片数等统计卡片
- **后台异步执行**：采集任务在后台线程执行，不阻塞页面操作

### 数据采集功能
- 采集会员列表（支持按最新、实名、VIP 等排序）
- 采集推荐会员（支持 menutype=2/3 分类，支持 lasttime 翻页）
- 采集"可能喜欢的人"推荐会员
- 采集会员详细信息（基本信息、择偶标准、照片等）
- 批量采集会员相册
- 采集幸福案例（成功脱单故事）
- 采集相亲活动
- 自动去重，避免重复数据
- 自动下载远程图片到本地存储

## 快速开始

### 后端启动

```bash
# 进入后端目录
cd xiangqin-backend

# 创建虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 前端启动

使用 HBuilderX 打开 `uni-app` 目录，运行到浏览器或小程序模拟器即可。

## API 接口

### 后端 API 列表

| 接口路径 | 方法 | 说明 |
|---------|------|------|
| `/api/tuodan/anli/` | GET | 获取幸福案例列表（支持分页） |
| `/api/tuodan/anli/` | POST | 新增幸福案例 |
| `/api/tuodan/images/<id>/` | GET | 获取案例图片 |
| `/api/tuodan/crawl/` | GET | 采集幸福案例数据 |
| `/api/tuodan/activity/` | GET | 获取/采集相亲活动 |
| `/api/users/` | GET | 获取用户列表（支持性别、城市过滤、排序） |
| `/api/users/crawl/` | GET | 采集用户列表数据（支持 menutype、lasttime 参数） |
| `/api/users/maylove/` | GET | 采集"可能喜欢的人"推荐会员 |
| `/api/users/getprofile/<id>/` | GET | 采集指定用户详细信息和相册 |
| `/api/users/photos/` | GET | 获取用户相册照片 |
| `/api/users/crawl/stats/` | GET | 爬取接口统计数据 |
| `/docs/` | GET | 在线 API 文档 |
| `/admin/` | GET | Django 管理后台 |
| `/admin/crawl/` | GET | Admin 一键采集管理页面 |

### 数据来源

项目数据采集自 [寿光相亲网](https://www.sgjhw.com)（潍然心动·寿光相亲网），采集内容包括：
- 会员列表（红娘推荐、最新注册、实名认证、VIP 会员）
- 会员详细信息（基本资料、择偶标准、个人照片等）
- 幸福案例（成功脱单故事）
- 相亲活动

## 许可证

本项目仅供学习交流使用。
