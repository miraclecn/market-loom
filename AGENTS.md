项目边界
不允许加入策略/回测/交易
稳定表名不能改
不允许提交 .env、DuckDB、真实数据
详细迁移规范见 docs/migration_from_alpha_data.md

阶段开发流程
每个迁移阶段不得直接在 main 上修改
每个阶段必须使用独立分支完成修改
每个阶段通过 PR 合并回 main
合并前必须完成该阶段可用的验证命令
alpha-data 仅作为只读参考源，个人使用、私有路径、真实凭证、真实数据、策略、回测、交易、模型训练相关内容不得迁移

阶段记录
- Phase 6: 使用 phase-6-test-migration 分支迁移合成测试夹具和回归测试，覆盖 normalized schema、prev_close、涨跌停价格基准、qfq fallback、行业 UNKNOWN/name fallback、单一行业层级、data_quality_usability_flags、research source contract、market data quality audit、CLI smoke；不得引入真实数据、凭证、网络访问、策略/回测/交易/模型训练内容。
