# 策略规划器前端

## 启动

```bash
npm install
npm run dev
```

默认地址：`http://localhost:5173`

## 联调后端

1. 在 `frontend` 目录创建 `.env` 文件：

```bash
VITE_API_BASE_URL=http://localhost:8000
```

2. 确保后端提供 `POST /run` 接口，入参示例：

```json
{
  "audit_task": "根据三份输入差异动态完成审核并输出结果",
  "quality_bar": "审核结果正确、覆盖关键差异、说明清晰",
  "pass_score": 90,
  "max_iterations": 3,
  "input_files": ["data/input_a.json", "data/input_b.json", "data/input_c.json"],
  "standard_file": "data/standard_answer.json"
}
```

未配置 `VITE_API_BASE_URL` 时，页面会使用 mock 结果展示完整流程。
