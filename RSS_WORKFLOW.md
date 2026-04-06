# RSS Workflow

当前复用入口：

```bash
cd /root/tencent_rsync_mac/RSS_article
bash ./run_rss_export.sh
```

## 当前配置

- 仓库目录：`/root/tencent_rsync_mac/RSS_article/lumen`
- 数据库：`/root/tencent_rsync_mac/RSS_article/lumen-data/feeds.db`
- 导出目录：`/root/tencent_rsync_mac/RSS_article/output`
- 导出结构：`订阅源/主题/YYYY-MM-DD 标题.md`
- 图片结构：与文章同级的 `文章名_assets/`

## 常用命令

查看当前订阅：

```bash
RSS_DB_PATH=/root/tencent_rsync_mac/RSS_article/lumen-data/feeds.db \
/root/tencent_rsync_mac/RSS_article/lumen/target/release/lumen list
```

添加订阅：

```bash
RSS_DB_PATH=/root/tencent_rsync_mac/RSS_article/lumen-data/feeds.db \
/root/tencent_rsync_mac/RSS_article/lumen/target/release/lumen add <feed-url>
```

取消订阅：

```bash
RSS_DB_PATH=/root/tencent_rsync_mac/RSS_article/lumen-data/feeds.db \
/root/tencent_rsync_mac/RSS_article/lumen/target/release/lumen remove <feed-id>
```

抓取更新：

```bash
RSS_DB_PATH=/root/tencent_rsync_mac/RSS_article/lumen-data/feeds.db \
/root/tencent_rsync_mac/RSS_article/lumen/target/release/lumen fetch
```

导出 Markdown 和本地图片：

```bash
bash /root/tencent_rsync_mac/RSS_article/run_rss_export.sh
```

## 当前订阅

- `2` `老布的AI知识库` `https://www.laobu.com/feed.xml`

## 说明

- 导出脚本文件：`/root/tencent_rsync_mac/RSS_article/export_lumen_to_output.py`
- 配置文件：`/root/tencent_rsync_mac/RSS_article/rss_export_config.json`
- `output/index.md` 是导出索引。
- 当前云端唯一订阅：`老布的AI知识库`
- 当前 `run_rss_export.sh` 已验证可以在云端重建文字导出。
- 图片本地化在本机和云端的行为不同：部分图片源会对云服务器 IP 返回 `403 Forbidden`。
- 为保持结果完整，当前云端 `output/` 已同步本机成功本地化图片后的导出结果。
