# SaaS 多租户隔离

## 模型
- 顶层 `tenants(租户)`；`saas_packages(套餐)`；`subscription_order/tenant_subscriptions(订阅)`
- 业务表全部带 `tenant_id`（String 36）并建索引
- 平台层：platform_user（运营商账号）不归属具体租户，管理全部租户/套餐

## 隔离三原则（改代码必守）
1. **写**：创建记录时强制写当前 `user.tenant_id`，**绝不信任请求体的租户字段**
2. **读**：所有列表/详情查询 `WHERE tenant_id = <当前租户>`，防跨租户取数
3. **校验**：UUID 路径参数 36 位正则校验后入库，防 `string_to_uuid` 报错

```python
# 正确示范
new = Foo(tenant_id=user.tenant_id, ...)      # 用 user 的，不用 body
rows = await db.query(Foo).filter(Foo.tenant_id == user.tenant_id).all()
```

## 平台运营管理
- 种子管理员：admin/admin123（admin@cenkor.cn），可获取 JWT 后直接 `/api/v1/*` e2e 测试
- 平台路由 `/api/platform/*` 处理租户入驻、套餐订阅、云端配置

## 订阅/套餐
- saas_package_tier、add_delivery_mode 等迁移维护套餐字段
- 租户订阅记录在 tenant_subscriptions
