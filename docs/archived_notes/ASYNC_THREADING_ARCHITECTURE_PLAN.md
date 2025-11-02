# 异步/线程混合架构改进方案

## 问题概述 (P0 Issue)

当前代码在 `app.py` 中混合使用 asyncio 和 threading,存在以下问题:

### 问题代码位置: app.py:316-370

```python
# 1. 在 Flask 请求上下文中创建新的 event loop
async def parse_document():
    parser = ParserManager()
    result = await parser.parse_document(...)
    return result

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
parse_result = loop.run_until_complete(parse_document())
loop.close()

# 2. 紧接着使用 threading.Thread 运行 pipeline
def run_pipeline():
    pipeline = TenderProcessingPipeline(...)
    result = pipeline.run_step(step)

thread = threading.Thread(target=run_pipeline, daemon=True)
thread.start()
```

### 问题分析

1. **Event Loop 管理不当**
   - 在每个请求中创建新的 event loop 效率低下
   - Flask 请求上下文不是为 asyncio 设计的
   - 可能与其他异步代码冲突

2. **线程混合使用风险**
   - asyncio 和 threading 混合使用容易出错
   - Daemon 线程无法保证任务完成
   - 没有统一的任务管理和监控

3. **缺乏任务持久化**
   - 进程重启后任务状态丢失
   - 无法跨进程/跨服务器共享任务
   - 难以实现任务重试和错误恢复

## 推荐解决方案

### 方案 1: Celery (推荐用于生产环境)

**优点:**
- 成熟的分布式任务队列
- 内置任务重试、定时任务、任务链
- 支持多种消息代理 (Redis, RabbitMQ)
- 强大的监控工具 (Flower)
- 完善的异步支持

**缺点:**
- 配置相对复杂
- 需要额外的 Redis/RabbitMQ 服务
- 学习曲线较陡

**实施步骤:**

1. **安装依赖**
```bash
pip install celery redis
```

2. **创建 Celery 应用** (`ai_tender_system/celery_app.py`)
```python
from celery import Celery

celery_app = Celery(
    'ai_tender_system',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时超时
)
```

3. **定义异步任务** (`ai_tender_system/tasks/tender_processing.py`)
```python
from celery import Task
from celery_app import celery_app
import asyncio

class AsyncTask(Task):
    """支持 asyncio 的 Celery Task"""
    def __call__(self, *args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.run_async(*args, **kwargs))
        finally:
            loop.close()

@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def process_tender_document(self, project_id, file_path, filter_model, extract_model):
    """处理标书文档的 Celery 任务"""
    try:
        # 1. 异步解析文档
        from modules.document_parser.parser_manager import ParserManager
        parser = ParserManager()
        parse_result = await parser.parse_document(
            doc_id=int(project_id),
            file_path=file_path
        )

        if parse_result.status.value != 'completed':
            raise Exception(f'文档解析失败: {parse_result.error_message}')

        # 2. 运行处理流程
        from modules.tender_processing.processing_pipeline import TenderProcessingPipeline
        pipeline = TenderProcessingPipeline(
            project_id=project_id,
            document_text=parse_result.content,
            filter_model=filter_model,
            extract_model=extract_model
        )

        # 保存 pipeline 实例
        from web.shared.instances import set_pipeline_instance
        set_pipeline_instance(pipeline.task_id, pipeline)

        # 执行步骤
        result = pipeline.run_step(1)

        return {
            'success': True,
            'task_id': pipeline.task_id,
            'result': result
        }
    except Exception as e:
        # 自动重试
        raise self.retry(exc=e, countdown=60)
```

4. **修改 Flask 路由** (app.py)
```python
from tasks.tender_processing import process_tender_document

@app.route('/api/tender-processing/start', methods=['POST'])
def start_tender_processing():
    """启动标书智能处理流程"""
    try:
        # ... 获取参数和保存文件 ...

        # 使用 Celery 异步执行
        task = process_tender_document.apply_async(
            args=[project_id, str(temp_file), filter_model, extract_model],
            task_id=f'tender_{project_id}_{int(time.time())}'
        )

        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': '处理任务已提交'
        })
    except Exception as e:
        logger.error(f"提交任务失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tender-processing/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """查询 Celery 任务状态"""
    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=celery_app)

    return jsonify({
        'success': True,
        'task_id': task_id,
        'state': result.state,
        'info': result.info,
        'ready': result.ready(),
        'successful': result.successful()
    })
```

5. **启动 Celery Worker**
```bash
# 开发环境
celery -A celery_app worker --loglevel=info

# 生产环境 (使用多进程)
celery -A celery_app worker --loglevel=info --concurrency=4

# 启动监控面板 (可选)
pip install flower
celery -A celery_app flower
```

### 方案 2: RQ (Redis Queue) - 简化版

**优点:**
- 配置简单,学习成本低
- 纯 Python,无需额外语言
- 轻量级,适合中小型项目

**缺点:**
- 功能相对 Celery 较少
- 依赖 Redis
- 异步支持需要额外处理

**实施步骤:**

1. **安装依赖**
```bash
pip install rq
```

2. **定义任务** (`ai_tender_system/tasks/tender_tasks.py`)
```python
import asyncio
from pathlib import Path

def process_tender_document_job(project_id, file_path, filter_model, extract_model):
    """RQ 任务:处理标书文档"""

    # 在任务中创建 event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        async def process():
            # 异步解析
            from modules.document_parser.parser_manager import ParserManager
            parser = ParserManager()
            result = await parser.parse_document(
                doc_id=int(project_id),
                file_path=file_path
            )
            return result

        parse_result = loop.run_until_complete(process())

        # 同步处理流程
        from modules.tender_processing.processing_pipeline import TenderProcessingPipeline
        pipeline = TenderProcessingPipeline(
            project_id=project_id,
            document_text=parse_result.content,
            filter_model=filter_model,
            extract_model=extract_model
        )

        from web.shared.instances import set_pipeline_instance
        set_pipeline_instance(pipeline.task_id, pipeline)

        result = pipeline.run_step(1)

        return {
            'success': True,
            'task_id': pipeline.task_id,
            'result': result
        }
    finally:
        loop.close()
```

3. **修改 Flask 路由**
```python
from redis import Redis
from rq import Queue

redis_conn = Redis()
rq_queue = Queue(connection=redis_conn)

@app.route('/api/tender-processing/start', methods=['POST'])
def start_tender_processing():
    """启动标书智能处理流程"""
    try:
        # ... 获取参数和保存文件 ...

        # 使用 RQ 提交任务
        from tasks.tender_tasks import process_tender_document_job
        job = rq_queue.enqueue(
            process_tender_document_job,
            project_id,
            str(temp_file),
            filter_model,
            extract_model,
            job_timeout='1h'
        )

        return jsonify({
            'success': True,
            'task_id': job.id,
            'message': '处理任务已提交'
        })
    except Exception as e:
        logger.error(f"提交任务失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

4. **启动 RQ Worker**
```bash
rq worker
```

### 方案 3: 保持当前方案但改进 (临时方案)

如果暂时无法引入外部任务队列,可以改进现有代码:

```python
# 1. 移除 asyncio,使用同步 ParserManager
from modules.document_parser.parser_manager import ParserManager

parser = ParserManager()
# 如果 parse_document 必须是异步的,可以在 ParserManager 内部处理
parse_result = parser.parse_document_sync(  # 添加同步版本
    doc_id=int(project_id),
    file_path=str(temp_file)
)

# 2. 改进线程管理
import concurrent.futures

executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

def run_pipeline():
    # ... pipeline 逻辑 ...
    pass

# 提交任务并获取 Future
future = executor.submit(run_pipeline)

# 可以设置回调
future.add_done_callback(lambda f: logger.info(f"任务完成: {f.result()}"))
```

## 实施建议

### 短期 (1-2周)

1. **使用方案 3** 快速改进现有代码
   - 移除不必要的 asyncio event loop 创建
   - 使用 ThreadPoolExecutor 替代裸线程
   - 添加适当的错误处理和日志

### 中期 (1-2月)

2. **采用方案 2 (RQ)**
   - 配置简单,快速上手
   - 提供基本的任务队列功能
   - 支持任务重试和监控

### 长期 (3月+)

3. **升级到方案 1 (Celery)**
   - 为生产环境做好准备
   - 支持更复杂的任务编排
   - 完善的监控和管理工具

## 迁移检查清单

- [ ] 安装所需依赖
- [ ] 配置 Redis/RabbitMQ (如需要)
- [ ] 创建任务定义文件
- [ ] 修改 Flask 路由,使用任务队列
- [ ] 添加任务状态查询端点
- [ ] 更新前端代码,轮询任务状态
- [ ] 测试任务执行、重试、失败恢复
- [ ] 部署 Worker 进程
- [ ] 配置监控和告警
- [ ] 更新部署文档

## 相关文件

- `ai_tender_system/web/app.py:316-370` - 当前问题代码
- `ai_tender_system/web/shared/instances.py` - Pipeline 实例管理
- `ai_tender_system/modules/document_parser/parser_manager.py` - 文档解析器
- `ai_tender_system/modules/tender_processing/processing_pipeline.py` - 处理流程

## 参考资料

- [Celery 官方文档](https://docs.celeryq.dev/)
- [RQ 官方文档](https://python-rq.org/)
- [Flask + Celery 集成指南](https://flask.palletsprojects.com/en/2.3.x/patterns/celery/)
