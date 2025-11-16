# 交互式图片故事生成系统 - Web界面

## 技术栈

- **React 18** - 用户界面框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **TailwindCSS** - 样式框架
- **Framer Motion** - 动画库
- **Zustand** - 状态管理
- **React Dropzone** - 文件上传

## 开发命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

## 项目结构

```
src/
├── components/        # React组件
│   ├── ImageUpload.tsx    # 图片上传组件
│   ├── StoryDisplay.tsx   # 故事显示组件
│   ├── ChoiceButton.tsx   # 选择按钮组件
│   └── ProgressBar.tsx    # 进度条组件
├── store/            # 状态管理
│   └── gameStore.ts       # 游戏状态
├── services/         # API服务
│   └── api.ts             # API接口
├── types/            # 类型定义
│   └── story.ts           # 故事相关类型
├── App.tsx           # 主应用组件
└── main.tsx          # 入口文件
```

## 核心功能

1. **图片上传** - 支持拖拽上传，实时预览
2. **故事展示** - 流式文本显示，场景图片展示
3. **选择交互** - 多样化选择按钮，不同类型选择
4. **进度追踪** - 故事进度和角色属性可视化
5. **响应式设计** - 适配桌面和移动设备

## 设计特点

- **沉浸式体验** - 深色主题，最小化干扰
- **流畅动画** - 页面切换和元素交互动画
- **直观操作** - 清晰的视觉反馈
- **无障碍支持** - 语义化HTML，键盘导航
