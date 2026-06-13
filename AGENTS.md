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
- Phase 7: 使用 phase-7-demo-fixture 分支添加 no-token demo fixture，生成 output/demo/raw.duckdb 与 output/demo/supplemental.duckdb，支持 build-research-source-db、check-research-source-contract、audit-market-data-quality、export-dashboard 端到端演示；输出文件由 gitignore 覆盖，不迁移真实数据、凭证、私有路径、策略/回测/交易/模型训练内容。
- Phase 8: 使用 phase-8-documentation 分支补齐公开文档，覆盖 quickstart、installation、data_sources、provider_setup、consumer_contract、research_source_schema、market_data_quality、dashboard、troubleshooting、release_checklist；文档必须使用 Market Loom / market-loom / market_loom 命名，不包含真实 token、真实账户、真实数据库路径、私有策略细节或真实数据转储。
- Phase 9: 使用 phase-9-ci 分支添加 GitHub Actions CI，覆盖 push 与 pull_request，Python 3.11/3.12，运行安装、pytest、market-loom --help、compileall 与 no-token demo smoke；CI 不依赖 provider credentials 或真实数据。
