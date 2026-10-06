# 权限与 ABAC

## 三层权限体系
1. **认证（我是谁）** — JWT，core/deps.py `get_current_user`
2. **RBAC（我能访问哪些功能）** — 用户→角色→权限点（code 如 `ai.use`、`permission.manage`）
3. **ABAC（我能访问哪些行的数据 + 哪些列能看全）** — services/abac/engine.py

## 功能权限（RBAC）
- 路由用 `require_permissions(["xxx.manage"])` 或 `require_any_permissions([...])` 门控
- 管理后台统一 `Depends(require_admin_portal_user)`
- 平台用户（SaaS 运营）走 `get_current_platform_user`

```python
# 示例
from app.core.deps import require_permissions

@router.get("/foo", dependencies=[Depends(require_permissions(["foo.view"]))])
async def list_foo(...): ...
```

## ABAC 数据权限（engine.py）
- `AbacContext` + `AbacEngine`
- **行级 scope**：`apply_row(query, resource)` 按资源解析 scope_type，动态拼查询条件，控制"数据可见范围"
- **列级脱敏**：
  ```python
  engine = abac(db, user)                     # services/abac/engine.py:305
  rows = engine.mask_rows(resource, rows)      # 统一脱敏敏感列
  ```
  - `field_mask/resource` 定义每个资源的脱敏列与规则
  - `mask_value/mask_type` 实现掩码（如姓名、电话、金额、手机号）
- 声明式守卫：`@abac_guard(resource)` 装饰器

## 约定
- **一切接口返回统一走 mask_rows**，前端/小程序不做二次脱敏（改规则不用发版）
- ABAC 管理后台路由挂在 `/api/admin/system/abac` 下
- 敏感资源：工资条(salary_slips)、客户/供应商、含 phone/net_amount/total_amount 等列
