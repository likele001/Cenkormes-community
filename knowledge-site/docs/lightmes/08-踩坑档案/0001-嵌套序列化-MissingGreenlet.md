# 0001- 嵌套关系序列化报 MissingGreenlet
- 日期：2026-09
- 模块：后端查询/序列化
- 严重度：🟡 中
- 状态：已解决

## 症状
`sqlalchemy.exc.MissingGreenlet`，接口 500，触发在返回嵌套关系（如客户带 contacts/addresses、BOM 带 items）时。

## 根因
异步 SQLAlchemy 中，给持久化对象取未加载的关联集合会触发懒加载，但异步会话没有 greenlet 上下文，直接抛错。

## 解决方案
查询就必须预加载关联：
```python
db.execute(stmt.options(selectinload(ErpCustomer.contacts),
                        selectinload(ErpCustomer.addresses)))
```

## 涉及文件
- 所有需要序列化嵌套关系的 list/detail 查询

## 预防
凡是接口要返回嵌套列表，一律在查询阶段 `.options(selectinload(...))` 预加载，不要在序列化阶段才取。
