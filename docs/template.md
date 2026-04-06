# 🔭 跨域周报 — 2026-03-01（第 9 周）

## 本周主旋律

**测不准的 AI × 测得准的市场**：西方 AI 实验室陷入评测体系的自指崩溃（越测越污染），中国 AI 生态直接用真实商业数据替代基准——千问 2 亿次下单、Kimi 20 天收入超去年全年。评估范式的东西方分叉，正在成为这个行业最被低估的结构性变量。

---

## AI Frontier 本周精华

1. **AI 评测体系自指崩溃** (02-26~28) — SWE-Bench 59% 任务不可解，GPT-5 CoT 引用"未来版本 Django API"；OpenAI 宣布停止报告旧基准。基准污染不是执行失误，是结构性宿命：每一个被发布的基准，最终都会被学会"如何通过"而非测量背后的真实能力。
   来源：[METR's Joel Becker on Exponential Time Horizons](https://www.latent.space/p/metr) · Latent Space

2. **VLA 推理性能成为新工程焦点** (02-23) — arXiv 出现 VLA-Perf benchmark，专测 Vision-Language-Action 模型推理速度。性能 benchmark 出现通常意味着一个技术领域从研究走向工程落地。
   来源：VLA-Perf: How Fast Can I Run My VLA · arXiv cs.RO

3. **Qwen3.5-122B 被社区认定为"本地最佳模型"** (02-27) — 72GB VRAM 可跑，多个独立测试在推理/编码/多模态上接近闭源 SOTA，可能改变企业 AI 采购决策（从 API 转向本地部署）。
   来源：[Qwen3.5 122B in 72GB VRAM is the best model available](https://www.reddit.com/r/LocalLLaMA/comments/1rf2ulo/) · Reddit LocalLLaMA · score 325

4. **DeepSeek V4 地缘政治风波** (02-27) — DeepSeek 给华为提供 V4 早期访问，排除 Nvidia/AMD。芯片供应链的 AI 侧已出现实质性地缘分叉。
   来源：[DeepSeek allows Huawei early access to V4, Nvidia/AMD excluded](https://www.reddit.com/r/LocalLLaMA/comments/1rf7m85/) · Reddit · score 327

5. **MCP 规范正式发布** (02-27) — Model Context Protocol 标准化 AI 工具调用协议，Anthropic/OpenAI/Google 生态共建信号。
   来源：[Specification — Model Context Protocol](https://modelcontextprotocol.io/specification/2025-11-25) · modelcontextprotocol.io

6. **软件开发瓶颈前移到"需求提取"** (02-23) — ReqElicitGym 论文前提：LLM coding 能力已强，现在瓶颈是搞清楚用户到底要什么。下一代 AI 编程工具的竞争点是"问清楚需求"，而非"写出代码"。
   来源：ReqElicitGym · arXiv cs.SE

---

## Startup & VC 本周精华

1. **分销即护城河，构建前先找渠道** (02-23) — AI 工具让构建门槛接近零，但分销门槛不变。案例：Tai Chi App 仅 YouTube 99K 订阅，4 个月达 $370k/月收入。判断创业机会的第一问应是"我有没有渠道"，而非"能否实现"。
   来源：Reddit r/entrepreneur · score 高相关集群

2. **AI 产品信任危机：情绪下滑 34%** (02-23) — 对 15,312 篇帖子分析：AI 产品用户满意度 120 天内下滑 34%，核心投诉是"质量退化"，而非技术局限。AI 产品竞争进入"好的 AI"分化期，纯噱头产品正在加速流失。
   来源：Reddit r/startups · "AI sentiment dropped 34% in 120 days"

3. **Anthropic 品牌反广告策略奏效** (02-23) — Super Bowl 期间 OpenAI/Google/Meta 投放广告，Anthropic 做反广告营销，品牌好感度反而上升 11%（BNP Paribas 数据）。
   来源：Reddit r/artificial · BNP Paribas 研究

4. **YC Spring 2026 批次窗口关闭** (02-23~27) — 本周大量 YC 申请总结帖，AI 工具类 / vertical SaaS 为主流方向，评审侧重真实用户数据而非 demo。

---

## 🔴 Alpha Signals 本周精华

- 🔴 **具身智能独角兽工厂开启**（02-28）— 单月内千寻智能获 20 亿融资，两天内两家具身智能公司达百亿估值，融资密度是商业化落地预期的前置信号，12 个月内将出现真实订单。
  来源：[千寻智能开年引爆具身智能赛道](https://www.qbitai.com/2026/02/381766.html) · 量子位；[两天诞生两家百亿独角兽](https://www.thepaper.cn/newsDetail_forward_32649366) · 澎湃新闻

- 🔴 **光互联/CPO 业绩兑现期**（02-28）— AI 算力驱动光通信需求变现，国内光模块企业净利最高预增 4 倍，主题行情已走但业绩确认阶段的确定性反而更高。
  来源：[AI算力驱动四家光企净利最高预增四倍](http://www.iccsz.com/4g/news.Asp?ID=b206d675e90e40b2afc10028a2dc6e00) · 讯石光通讯网

- 🔴 **40 万亿险资入场 A 股 AI 板块**（02-27）— 险资是 A 股最大长线资金，配置行为具有黏性，单日 100 亿主力净流入，意味着 AI 算力主线有持续资金面支撑。
  来源：[40万亿险资跑步入场](https://wap.eastmoney.com/a/202602253654148368.html) · 东方财富

- ⚠️ **关税政策双重跳跃**（02-23）— 最高法院推翻关税令后，特朗普绕过司法将全球关税升至 15%。进口通胀压力上升，压制降息节奏，对利率敏感板块形成估值压力；供应链外迁受益方值得重新定价。

- ⚠️ **黄金创史上最长连涨纪录**（02-23）— 连续 8 个月上涨，央行购金量历史新高，主权财富基金战略配置转变信号极强。黄金矿企 Beta 放大效应值得关注（GDX/GDXJ，紫金矿业 02899.HK）。

- 💊 **AlphaFold 后时代：AI×Biotech Alpha 折扣正在消失**（02-28）— DeepMind 子公司发布"AlphaFold 4 级别"新模型；清华 AI 药物筛选提速百万倍登 Science。散户忽视，机构悄悄布局。
  来源：[DeepMind新模型](https://www.huxiu.com/article/4837026.html) · 虎嗅；[清华AI找药登Science](https://hub.baai.ac.cn/view/51774) · BAAI

---

## China Tech 本周精华

1. **千问 Agent 商业化里程碑：近 2 亿次真实下单** (02-23) — 春节期间用自然语言完成餐饮/机票/电影票交易，意图理解→垂直服务调用→支付的完整 Agent 链路验证成功。这是国内 LLM 从"对话产品"走向"任务执行平台"最清晰的里程碑。
   来源：36氪报道 · 春节 AI 大战复盘

2. **Kimi K2.5：20 天收入超去年全年** (02-23) — OpenRouter 数据显示 K2.5 调用量领先，印证"推理能力提升→开发者 API 采用量飙升→商业化正循环"路径可行。月之暗面推进新一轮 7 亿美元融资，估值超 100 亿美元。
   来源：[月之暗面融资进展](http://www.cb.com.cn/index/show/zj/cv/cv135348501260) · 中国经营网；[AI四小龙出海热潮](https://m.thepaper.cn/newsDetail_forward_32668523) · 澎湃新闻

3. **工信部发布首个人形机器人国家标准** (03-01) — 《人形机器人与具身智能标准体系（2026版）》覆盖全产业链，标准化是工业化的前置条件，供应链分工博弈正式开始。
   来源：[首个国家级标准发布](https://36kr.com/newsflashes/3702620480172423?f=rss) · 36氪

4. **豆包/千问/Kimi 三条 AI Agent 路线分叉** (03-01) — 豆包聚焦泛娱乐+社交，千问押注电商+硬件入口（MWC 2026 发布 AI 眼镜），Kimi 走纯 AI 效率工具+出海。分化是健康的产业格局信号。
   来源：[站在AI Agent的岔路口](https://www.donews.com/article/detail/6399/95788.html) · DoNews；[千问将发布AI眼镜](https://36kr.com/p/3702628151751046?f=rss) · 36氪

5. **AI 客服被"真人+低价"打败**（03-01）— V2EX 案例：100 家店客户从 AI 客服（月付 7500 元）切换到真人（月付 3000 元/人）。AI 的护城河不是"比人便宜"，而是"7x24+0 培训成本+数据沉淀"。
   来源：[公司的AI客服被真人干掉了](https://www.v2ex.com/t/1194797) · V2EX

---

## 🎙️ Podcast 本周洞察

1. **Hidden Brain《Do You Feel Invisible?》** — Anti-mattering（感觉自己毫不重要）与抑郁的相关，**强于** mattering 与心理健康的正向相关。方向不对称：被无视的伤害大于被珍视的益处。组织推论：强调正向反馈不够，真正关键是"让人感到说话有人听"。

2. **Latent Space 三集连发：AI 评测的认识论危机** — 测量即训练，训练即测量，这个边界已消失。METR 时间视野图呈现能力线性增长（四个月翻倍），但感知层面因"阈值效应"制造非连续感。最诚实的结论：我们在用为"静态竞争性产品市场"设计的评测框架，试图理解一个动态演化的学习系统。

3. **20VC《Codex vs Claude Code vs Cursor》(Alex Embiricos)** — AI 编程的真正瓶颈不是模型，而是"人类打字和验证速度"。从配对工作到多 agent 并行委托：工程师的核心技能从执行力转向判断力（knowing when to step in）。

4. **Knowledge Project《$2T Mind — Nicolai Tangen》** — 挪威主权基金 CEO：先建仓再做研究（仓位创造紧迫性）；最难的事是什么都不做，但往往是正确的。预测正在变得无用——这个结论放在 AI 时代尤其尖锐。

5. **Naval Podcast《A Motorcycle for the Mind》** — "AI 适应人类的速度比人类适应 AI 快得多，界面演化的压力是单向的。"这不是便利性问题——这是 confirmation bias 的基础设施化：如果 AI 完全适应你的思维，你的思维就不再被挑战。

---

## 🔗 跨域连接（本周最重要）

### 连接 1：委托革命 × Anti-mattering——AI 工具的下一代战场是"让工程师感到说话有人听"

**AI 编程信号**：Alex Embiricos 描述从"配对工作"到"多 agent 并行委托"的转变，工程师从执行者变为判断者（knowing when to step in）。
来源：[20VC · Codex vs Claude Code vs Cursor](https://thetwentyminutevc.libsyn.com/20vc-codex-vs-claude-code-vs-cursor-who-wins-who-loses-will-all-coding-be-automated-do-we-need-pms-the-real-bottleneck-to-agi-the-three-phases-of-agents-and-what-you-need-to-know-with-alex-embiricos-head-of-codex-at-openai)

**Podcast 洞察**：Hidden Brain《Do You Feel Invisible?》——Anti-mattering 链条：发言被无视→介入信号被忽略→隐性低效积累→突然离职。在组织中，这条路径的温和变体正在 AI 时代的工程团队中悄悄激活。

**跨域推论**：AI 编程工具的竞争目前聚焦于"让委托更顺畅"，但下一个真正的差异化点可能是**反馈设计**——工程师的判断意见是否被 AI 真实接收并体现在后续行为中。一个让工程师感到"说了但没用"的 AI，会系统性积累 anti-mattering，即使它的代码写得很好。这是一个尚未有人在讨论的产品方向。

**创业机会**：专注于"AI 工作流中的工程师反馈可见性"工具——让工程师知道他们的介入和判断实际上改变了 AI 的行为轨迹。

---

### 连接 2：AI 评测自指崩溃 × 中国 AI 用"真实订单"替代基准——下一代能力评估范式来自东方？

**AI Frontier 信号**：SWE-Bench 崩溃，GPT-5 CoT 背答案，基准污染是结构性宿命——当指标成为目标，它就不再是好指标（古德哈特定律在 AI 中的必然显现）。
来源：[Latent Space · Anthropic Distillation & How Models Cheat](https://www.latent.space/p/paid-anthropic-distillation-and-how)

**China Tech 信号**：千问用"近 2 亿次真实下单"证明 Agent 能力；Kimi 用"20 天收入超去年全年"证明商业化可行性。没有 benchmark，直接用市场结果说话。
来源：[36氪 · 春节AI大战复盘]；[澎湃新闻 · AI四小龙出海热潮](https://m.thepaper.cn/newsDetail_forward_32668523)

**跨域推论**：这两个信号放在一起，暗示 AI 能力评估的下一代范式可能从西方实验室的 benchmark 工程转向东方商业化实践中的真实市场结果验证。"能完成多少真实交易"比"SWE-Bench 得分"更难污染，因为用户不会为了帮助 AI 作弊而花钱下单。

**投资含义**：当西方 AI 公司在争论评测方法论时，中国 AI 公司已经在构建真实的商业闭环。这个执行速度差，在 AI Agent 商业化赛道上可能是决定性的。

---

### 连接 3：VLA 工程化 × SaaS 结构性重估——AI 正在从工具变成基础设施

**AI Frontier 信号**：VLA-Perf benchmark 出现（具身 AI 推理性能工程化），小米开源首代机器人 VLA 大模型，国家标准体系发布。
来源：VLA-Perf · arXiv；[工信部标准](https://36kr.com/newsflashes/3702620480172423?f=rss) · 36氪

**Alpha Signals 信号**：SaaS 板块 Q4 2025 NRR 开始下降，AI 替代风险最高的是"无差异化 workflow SaaS"（CRM、HR tech、项目管理工具）。
来源：Reddit r/SecurityAnalysis · "SaaS Meltdown or overreaction?" · score 72

**跨域推论**：VLA 工程化（AI 进入机器人基础设施）和 SaaS NRR 下降（AI 替代软件访问权）是同一底层趋势的两个截面——AI 正在从"工具层"下沉到"基础设施层"，原来"卖软件访问权"的商业模式正被"直接完成任务"替代。SaaS 公司的分化点：**是否具备 AI 无法轻易替代的合规/数据黏性**（网络安全 SaaS > workflow SaaS）。

---

## 本周未解之问

1. **如果 AI 编程工具让工程师从执行者变为判断者，"判断力"从哪里来？** 没有足够执行经验积累的新人，判断力如何培养——AI 编程工具对有经验者是杠杆，对新手是否是陷阱？（来自 [20VC · Embiricos](https://thetwentyminutevc.libsyn.com/20vc-codex-vs-claude-code-vs-cursor-who-wins-who-loses-will-all-coding-be-automated-do-we-need-pms-the-real-bottleneck-to-agi-the-three-phases-of-agents-and-what-you-need-to-know-with-alex-embiricos-head-of-codex-at-openai) + Hidden Brain）

2. **所有公开基准最终都会被污染——但不发布基准则无法形成行业共识。这个公地悲剧如何破局？** 私有基准的权力集中问题是否比污染问题更严重？（来自 [Latent Space · METR](https://www.latent.space/p/metr)）

3. **中国具身智能赛道本月两家百亿独角兽，融资密度是信号还是泡沫？** 标准体系刚发布，真实订单在哪里？（来自 [量子位 · 千寻智能](https://www.qbitai.com/2026/02/381766.html) + [36氪 · 标准发布](https://36kr.com/newsflashes/3702620480172423?f=rss)）

---

## 下周关注

1. **MWC 2026（3 月 2 日）千问 AI 眼镜发布** — 国内 AI 大厂首次正面硬刚 Meta Ray-Ban，关注产品形态和发布现场反应，这是硬件+Agent 路线的首次公开验证。

2. **DeepSeek V4 + Qwen3.5 对抗升级** — DeepSeek 给华为独家早期访问、Qwen3.5-122B 本地部署持续出圈，两者共同压缩美国闭源模型在企业端的定价权。下周关注 Nvidia/AMD 是否有回应动作。

3. **AI 评测体系替代方案** — METR 时间视野图方法论首次公开，下周关注是否有其他实验室跟进采用，或对"任务时长"作为能力单位的批评。

---

*Intel 数据：OneDrive/intel data/reports/2026-02-23 ~ 2026-03-01 | Podcast 数据：OneDrive/podcast data/daily/briefing/2026-02-23 ~ 2026-03-01*
*Watch 模块：ai-frontier ×6天，startup-vc ×7天，alpha-signals ×7天，china-tech ×7天*
*Podcast：13 集深入，~28 集全景扫描（2026-02-23、02-28、03-01 三份简报）*
*生成时间：2026-03-01 | Lumen — Intel Synthesis v1.0*
