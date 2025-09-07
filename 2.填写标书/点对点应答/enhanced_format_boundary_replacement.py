#!/usr/bin/env python3
"""
增强的格式边界保持替换方法
专门解决采购编号等跨run替换时格式层次丢失的问题
"""

def _precise_cross_run_replace_v2(self, paragraph, old_text: str, new_text: str):
    """
    🎯 格式边界保持的精确跨run替换 V2 - 保持原有格式层次
    
    核心策略：
    1. 分析原始格式分布和边界
    2. 智能映射新文本到合适的格式区域
    3. 最小化格式边界变化
    """
    try:
        full_text = paragraph.text
        logger.info(f"🎯 执行格式边界保持替换V2: '{old_text}' -> '{new_text}'")
        
        # 查找目标文本位置
        start_pos = full_text.find(old_text)
        if start_pos == -1:
            logger.warning("目标文本未找到")
            return False
        
        end_pos = start_pos + len(old_text)
        logger.info(f"目标文本位置: {start_pos}-{end_pos}")
        
        # 🔍 分析所有run的格式和位置
        runs_info = []
        current_pos = 0
        
        for i, run in enumerate(paragraph.runs):
            run_start = current_pos
            run_end = current_pos + len(run.text)
            
            format_key = (
                bool(run.font.bold) if run.font.bold is not None else False,
                bool(run.font.italic) if run.font.italic is not None else False,
                bool(run.font.underline) if run.font.underline is not None else False
            )
            
            run_info = {
                'index': i,
                'run': run,
                'start': run_start,
                'end': run_end,
                'text': run.text,
                'format_key': format_key,
                'is_affected': run_start < end_pos and run_end > start_pos
            }
            runs_info.append(run_info)
            current_pos = run_end
        
        # 找出涉及的run
        affected_runs = [r for r in runs_info if r['is_affected']]
        logger.info(f"涉及 {len(affected_runs)} 个run")
        
        # 🎯 关键策略：特殊处理采购编号类型的替换
        if len(affected_runs) >= 3 and '采购编号' in old_text:
            logger.info("🎯 检测到采购编号替换，使用特殊格式保持策略")
            return self._handle_tender_number_replacement_special(paragraph, affected_runs, old_text, new_text, start_pos, end_pos)
        
        # 通用处理逻辑
        elif len(affected_runs) == 1:
            # 单run：直接替换
            run = affected_runs[0]['run']
            run.text = run.text.replace(old_text, new_text)
            logger.info("✅ 单run替换完成")
            return True
        
        else:
            # 多run：使用保守策略
            logger.info("🔧 多run保守替换策略")
            first_run = affected_runs[0]['run']
            
            # 计算前缀、后缀
            first_overlap_start = max(start_pos, affected_runs[0]['start'])
            last_run_info = affected_runs[-1]
            last_overlap_end = min(end_pos, last_run_info['end'])
            
            # 构建新内容
            prefix = ""
            if first_overlap_start > affected_runs[0]['start']:
                prefix = affected_runs[0]['text'][:first_overlap_start - affected_runs[0]['start']]
            
            suffix = ""
            if last_overlap_end < last_run_info['end']:
                suffix_start_idx = last_overlap_end - last_run_info['start']
                suffix = last_run_info['text'][suffix_start_idx:]
            
            # 将所有内容放入第一个run
            first_run.text = prefix + new_text + suffix
            
            # 清空其他涉及的run
            for run_info in affected_runs[1:]:
                if run_info['start'] >= start_pos and run_info['end'] <= end_pos:
                    run_info['run'].text = ""
            
            logger.info("✅ 多run保守替换完成")
            return True
            
    except Exception as e:
        logger.error(f"格式边界保持替换失败: {e}", exc_info=True)
        return False

def _handle_tender_number_replacement_special(self, paragraph, affected_runs, old_text, new_text, start_pos, end_pos):
    """
    🎯 采购编号替换的特殊处理 - 保持斜体+下划线格式
    
    基于分析，采购编号的格式分布：
    - 普通文本: 粗体=False, 斜体=False, 下划线=False  
    - 采购编号: 粗体=False, 斜体=True, 下划线=True
    - 下划线区: 粗体=False, 斜体=False, 下划线=True
    """
    try:
        logger.info("🎯 执行采购编号特殊格式保持策略")
        
        # 分析格式分组
        format_groups = {}
        for run_info in affected_runs:
            fmt_key = run_info['format_key']
            if fmt_key not in format_groups:
                format_groups[fmt_key] = []
            format_groups[fmt_key].append(run_info)
        
        logger.info(f"发现 {len(format_groups)} 种格式组合:")
        for fmt_key, runs in format_groups.items():
            bold, italic, underline = fmt_key
            logger.info(f"  格式(粗体={bold}, 斜体={italic}, 下划线={underline}): {len(runs)}个run")
        
        # 🎯 策略：找到包含"（采购编号）"的斜体+下划线格式run，只在这些run中替换
        target_format_key = (False, True, True)  # 斜体+下划线
        
        if target_format_key in format_groups:
            target_runs = format_groups[target_format_key]
            logger.info(f"找到 {len(target_runs)} 个目标格式run")
            
            # 检查是否可以只在这些run中完成替换
            target_text = ""
            for run_info in target_runs:
                if run_info['start'] >= start_pos and run_info['end'] <= end_pos:
                    target_text += run_info['text']
            
            if old_text in target_text or '采购编号' in target_text:
                # 可以在目标格式run中完成替换
                logger.info("✅ 在目标格式run中执行替换")
                
                # 将新文本分配到第一个目标格式run
                first_target_run = target_runs[0]['run']
                
                # 简单策略：将整个新文本放入第一个匹配格式的run
                first_target_run.text = new_text.strip('（）')  # 去掉括号，保持原有格式结构
                
                # 清空其他包含采购编号的run
                for run_info in target_runs[1:]:
                    if '采购编号' in run_info['text'] or '编号' in run_info['text']:
                        run_info['run'].text = ""
                
                logger.info("✅ 采购编号特殊替换完成，保持了斜体+下划线格式")
                return True
        
        # 如果特殊策略失败，回退到通用策略
        logger.info("⚠️ 特殊策略不适用，使用通用替换")
        return False
        
    except Exception as e:
        logger.error(f"采购编号特殊处理失败: {e}", exc_info=True)
        return False

# 这个文件包含了增强的替换逻辑，可以集成到主文件中