# <模块> · <接口名>
- 路径：`/api/admin/<模块>/...`
- 方法：GET / POST / PUT / DELETE / PATCH
- 权限：需要的 role / 是否租户隔离
- 文档来源：后端 openapi（由 scan 自动生成基线补充）

## 请求参数
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tenant_id | string | 否 | 服务端强制取当前租户 |

## 响应示例
```json
{}
```

## 注意事项
- UUID 路径参数做 36 位正则校验
- 列表过滤 WHERE tenant_id = 当前租户
- 敏感字段返回前经 mask_rows 脱敏
