# 1012D Business Model Driven Preview Page Upgrade

## 结论

`1012D` 已把 `1012C` 的业务对象和 surface 合同压进 `frontend/xiaojiao-preview.html`。这一步只升级 preview route，不切默认入口，不接 provider，不写正式库。

## 已进入页面的业务对象

| work_object | 进入位置 | 当前形态 |
| --- | --- | --- |
| lesson_design | 首页、单课焦点 | 课时草稿确认 |
| lesson_section | 单课焦点 | 第二环节时间调整候选 |
| handout | 首页、单课焦点、本课材料夹、候选审核 | 学习单候选 |
| rubric | 首页、单课焦点、本课材料夹、候选审核 | 评价量规 preview stub |
| resource_reference | 首页、单课焦点、本课材料夹、候选审核 | 资源参考 preview stub |
| evidence_note | 单课焦点、本课材料夹 | 轻记录 |
| teacher_review_gate | 单课焦点、候选审核 | 教师审核门 |
| agent_long_task | 旧入口 | 弱入口，不做默认主视觉 |

## 页面变化

| surface | 页面段 | 业务变化 |
| --- | --- | --- |
| home_light_entry | `entry` | 增加业务进度、review queue、材料夹状态、弱旧入口 |
| single_lesson_focus | `focus` | 增加本课材料夹、评价量规 stub、资源参考 stub、轻记录、teacher_review_gate 可见状态 |
| lesson_material_folder | `material` | 新增本课材料夹，集中呈现 handout / rubric / resource_reference / evidence_note |
| candidate_review_surface | `candidate` | 支持学习单、评价量规、资源参考三类候选预览 |
| legacy_deep_task_entry | `legacy` | bot_chat / 旧长任务 / 作业提交机只保留弱入口 |

## 边界

- `preview_route_only=true`
- `default_route_changed=false`
- `legacy_agent_as_default=false`
- `old_strong_agent_page_preserved=true`
- `teacher_review_required=true`
- `formal_apply_performed=false`
- `real_database_written=false`
- `memory_written=false`
- `Feishu_written=false`
- `batch_generation_allowed=false`
- `background_generation_allowed=false`
- `new_live_provider_call=false`

## 输出

- `frontend/xiaojiao-preview.html`
- `samples/xiaojiao_business_model_driven_preview_page_upgrade_1012D/*.json`
- `scripts/validate_xiaojiao_business_model_driven_preview_page_upgrade_1012D.py`
- `docs/audit/xiaojiao_business_model_driven_preview_page_upgrade_1012D_result.json`
- `docs/audit/xiaojiao_business_model_driven_preview_page_upgrade_1012D_report.md`
- `docs/audit_packages/xiaojiao_business_model_driven_preview_page_upgrade_1012D_manifest.json`
- `docs/audit_packages/xiaojiao_business_model_driven_preview_page_upgrade_1012D.zip`

## 状态

```text
XIAOJIAO_BUSINESS_MODEL_DRIVEN_PREVIEW_PAGE_UPGRADE_PASS
ALL_1012D_BUSINESS_MODEL_DRIVEN_PREVIEW_PAGE_UPGRADE_CHECKS_OK
```
