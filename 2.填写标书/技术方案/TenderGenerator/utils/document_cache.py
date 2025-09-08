"""
智能文档缓存系统
用于缓存解析结果、匹配结果和生成内容，提升系统性能
"""

import os
import json
import hashlib
import pickle
import time
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import threading

class DocumentCache:
    """文档缓存管理类"""
    
    def __init__(self, cache_dir: str = "cache", max_cache_size_mb: int = 500):
        """
        初始化文档缓存
        
        Args:
            cache_dir: 缓存目录
            max_cache_size_mb: 最大缓存大小（MB）
        """
        self.cache_dir = Path(cache_dir)
        self.max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        self.logger = logging.getLogger(__name__)
        self._lock = threading.RLock()
        
        # 创建缓存目录
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 缓存子目录
        self.parsed_docs_dir = self.cache_dir / "parsed_docs"
        self.matches_dir = self.cache_dir / "matches"
        self.content_dir = self.cache_dir / "content"
        self.quality_dir = self.cache_dir / "quality"
        
        for dir_path in [self.parsed_docs_dir, self.matches_dir, self.content_dir, self.quality_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 缓存索引文件
        self.index_file = self.cache_dir / "cache_index.json"
        self.cache_index = self._load_cache_index()
        
        self.logger.info(f"文档缓存系统初始化完成: {self.cache_dir}")
    
    def _load_cache_index(self) -> Dict[str, Any]:
        """加载缓存索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"加载缓存索引失败: {e}")
        
        return {
            'parsed_docs': {},
            'matches': {},
            'content': {},
            'quality_assessments': {},
            'last_cleanup': time.time()
        }
    
    def _save_cache_index(self):
        """保存缓存索引"""
        with self._lock:
            try:
                with open(self.index_file, 'w', encoding='utf-8') as f:
                    json.dump(self.cache_index, f, ensure_ascii=False, indent=2)
            except Exception as e:
                self.logger.error(f"保存缓存索引失败: {e}")
    
    def _get_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        try:
            hasher = hashlib.md5()
            
            # 添加文件路径
            hasher.update(file_path.encode('utf-8'))
            
            # 添加文件修改时间和大小
            stat = os.stat(file_path)
            hasher.update(str(stat.st_mtime).encode('utf-8'))
            hasher.update(str(stat.st_size).encode('utf-8'))
            
            return hasher.hexdigest()
        except Exception as e:
            self.logger.warning(f"计算文件哈希失败: {e}")
            return hashlib.md5(f"{file_path}_{time.time()}".encode()).hexdigest()
    
    def _get_content_hash(self, content: Any) -> str:
        """计算内容哈希值"""
        try:
            if isinstance(content, (dict, list)):
                content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
            else:
                content_str = str(content)
            
            return hashlib.md5(content_str.encode('utf-8')).hexdigest()
        except Exception:
            return hashlib.md5(str(time.time()).encode()).hexdigest()
    
    def cache_parsed_document(self, file_path: str, parsed_data: Dict[str, Any]) -> bool:
        """
        缓存文档解析结果
        
        Args:
            file_path: 文档路径
            parsed_data: 解析结果
            
        Returns:
            缓存是否成功
        """
        with self._lock:
            try:
                file_hash = self._get_file_hash(file_path)
                cache_file = self.parsed_docs_dir / f"{file_hash}.json"
                
                # 保存解析结果
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(parsed_data, f, ensure_ascii=False, indent=2)
                
                # 更新索引
                self.cache_index['parsed_docs'][file_path] = {
                    'hash': file_hash,
                    'cache_file': str(cache_file),
                    'cached_at': time.time(),
                    'size': cache_file.stat().st_size
                }
                
                self._save_cache_index()
                self.logger.debug(f"文档解析结果已缓存: {file_path}")
                return True
                
            except Exception as e:
                self.logger.error(f"缓存文档解析结果失败: {e}")
                return False
    
    def get_cached_parsed_document(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存的文档解析结果
        
        Args:
            file_path: 文档路径
            
        Returns:
            解析结果，如果缓存不存在或过期返回None
        """
        with self._lock:
            try:
                cache_info = self.cache_index['parsed_docs'].get(file_path)
                if not cache_info:
                    return None
                
                # 检查文件是否改变
                current_hash = self._get_file_hash(file_path)
                if current_hash != cache_info['hash']:
                    # 文件已更改，移除缓存
                    self._remove_cached_item('parsed_docs', file_path)
                    return None
                
                # 读取缓存
                cache_file = Path(cache_info['cache_file'])
                if cache_file.exists():
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.logger.debug(f"使用缓存的文档解析结果: {file_path}")
                    return data
                else:
                    # 缓存文件不存在，移除索引
                    self._remove_cached_item('parsed_docs', file_path)
                    return None
                    
            except Exception as e:
                self.logger.warning(f"获取缓存文档解析结果失败: {e}")
                return None
    
    def cache_matches(self, requirements: List[Dict], features: List[Dict], matches: List[Dict[str, Any]]) -> bool:
        """
        缓存匹配结果
        
        Args:
            requirements: 需求列表
            features: 功能列表
            matches: 匹配结果
            
        Returns:
            缓存是否成功
        """
        with self._lock:
            try:
                # 生成匹配缓存键
                req_hash = self._get_content_hash(requirements)
                feat_hash = self._get_content_hash(features)
                match_key = f"{req_hash}_{feat_hash}"
                
                cache_file = self.matches_dir / f"{match_key}.pickle"
                
                # 保存匹配结果
                with open(cache_file, 'wb') as f:
                    pickle.dump(matches, f)
                
                # 更新索引
                self.cache_index['matches'][match_key] = {
                    'cache_file': str(cache_file),
                    'cached_at': time.time(),
                    'size': cache_file.stat().st_size,
                    'requirements_count': len(requirements),
                    'features_count': len(features),
                    'matches_count': len(matches)
                }
                
                self._save_cache_index()
                self.logger.debug(f"匹配结果已缓存: {len(matches)} 个匹配")
                return True
                
            except Exception as e:
                self.logger.error(f"缓存匹配结果失败: {e}")
                return False
    
    def get_cached_matches(self, requirements: List[Dict], features: List[Dict]) -> Optional[List[Dict[str, Any]]]:
        """
        获取缓存的匹配结果
        
        Args:
            requirements: 需求列表
            features: 功能列表
            
        Returns:
            匹配结果，如果缓存不存在返回None
        """
        with self._lock:
            try:
                req_hash = self._get_content_hash(requirements)
                feat_hash = self._get_content_hash(features)
                match_key = f"{req_hash}_{feat_hash}"
                
                cache_info = self.cache_index['matches'].get(match_key)
                if not cache_info:
                    return None
                
                cache_file = Path(cache_info['cache_file'])
                if cache_file.exists():
                    with open(cache_file, 'rb') as f:
                        matches = pickle.load(f)
                    
                    self.logger.debug(f"使用缓存的匹配结果: {len(matches)} 个匹配")
                    return matches
                else:
                    # 缓存文件不存在，移除索引
                    self._remove_cached_item('matches', match_key)
                    return None
                    
            except Exception as e:
                self.logger.warning(f"获取缓存匹配结果失败: {e}")
                return None
    
    def cache_generated_content(self, 
                              requirement: str, 
                              feature: str, 
                              section_title: str,
                              content: str,
                              quality_info: Dict[str, Any]) -> bool:
        """
        缓存生成内容
        
        Args:
            requirement: 需求描述
            feature: 功能描述
            section_title: 章节标题
            content: 生成的内容
            quality_info: 质量信息
            
        Returns:
            缓存是否成功
        """
        with self._lock:
            try:
                # 生成内容缓存键
                content_key = self._get_content_hash(f"{requirement}_{feature}_{section_title}")
                cache_file = self.content_dir / f"{content_key}.json"
                
                cache_data = {
                    'requirement': requirement,
                    'feature': feature,
                    'section_title': section_title,
                    'content': content,
                    'quality_info': quality_info,
                    'cached_at': time.time()
                }
                
                # 保存内容
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
                # 更新索引
                self.cache_index['content'][content_key] = {
                    'cache_file': str(cache_file),
                    'cached_at': time.time(),
                    'size': cache_file.stat().st_size,
                    'section_title': section_title,
                    'quality_score': quality_info.get('quality_score', 0.0)
                }
                
                self._save_cache_index()
                self.logger.debug(f"生成内容已缓存: {section_title}")
                return True
                
            except Exception as e:
                self.logger.error(f"缓存生成内容失败: {e}")
                return False
    
    def get_cached_generated_content(self, 
                                   requirement: str, 
                                   feature: str, 
                                   section_title: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存的生成内容
        
        Args:
            requirement: 需求描述
            feature: 功能描述
            section_title: 章节标题
            
        Returns:
            包含内容和质量信息的字典，如果缓存不存在返回None
        """
        with self._lock:
            try:
                content_key = self._get_content_hash(f"{requirement}_{feature}_{section_title}")
                cache_info = self.cache_index['content'].get(content_key)
                
                if not cache_info:
                    return None
                
                cache_file = Path(cache_info['cache_file'])
                if cache_file.exists():
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # 检查缓存是否过期 (24小时)
                    if time.time() - cache_data.get('cached_at', 0) > 24 * 3600:
                        self._remove_cached_item('content', content_key)
                        return None
                    
                    self.logger.debug(f"使用缓存的生成内容: {section_title}")
                    return {
                        'content': cache_data['content'],
                        'quality_info': cache_data['quality_info']
                    }
                else:
                    self._remove_cached_item('content', content_key)
                    return None
                    
            except Exception as e:
                self.logger.warning(f"获取缓存生成内容失败: {e}")
                return None
    
    def _remove_cached_item(self, category: str, key: str):
        """移除缓存项"""
        try:
            if key in self.cache_index[category]:
                cache_info = self.cache_index[category][key]
                cache_file = Path(cache_info['cache_file'])
                
                if cache_file.exists():
                    cache_file.unlink()
                
                del self.cache_index[category][key]
                self._save_cache_index()
                
        except Exception as e:
            self.logger.warning(f"移除缓存项失败: {e}")
    
    def cleanup_cache(self, force: bool = False):
        """
        清理过期和过大的缓存
        
        Args:
            force: 是否强制清理
        """
        with self._lock:
            current_time = time.time()
            last_cleanup = self.cache_index.get('last_cleanup', 0)
            
            # 如果距离上次清理不足1小时且非强制清理，跳过
            if not force and current_time - last_cleanup < 3600:
                return
            
            self.logger.info("开始清理缓存...")
            
            # 计算当前缓存大小
            total_size = self._calculate_cache_size()
            
            if total_size > self.max_cache_size_bytes:
                self.logger.info(f"缓存大小 ({total_size / 1024 / 1024:.1f}MB) 超过限制，开始清理")
                
                # 收集所有缓存项并按时间排序
                all_items = []
                for category, items in self.cache_index.items():
                    if category in ['parsed_docs', 'matches', 'content', 'quality_assessments']:
                        for key, info in items.items():
                            all_items.append((category, key, info.get('cached_at', 0), info.get('size', 0)))
                
                # 按缓存时间排序，删除最旧的
                all_items.sort(key=lambda x: x[2])
                
                # 删除缓存直到大小合适
                for category, key, cached_at, size in all_items:
                    if total_size <= self.max_cache_size_bytes * 0.8:  # 清理到80%
                        break
                    
                    self._remove_cached_item(category, key)
                    total_size -= size
            
            # 清理过期缓存（超过7天）
            expire_time = current_time - 7 * 24 * 3600
            expired_items = []
            
            for category, items in self.cache_index.items():
                if category in ['parsed_docs', 'matches', 'content', 'quality_assessments']:
                    for key, info in items.items():
                        if info.get('cached_at', 0) < expire_time:
                            expired_items.append((category, key))
            
            for category, key in expired_items:
                self._remove_cached_item(category, key)
            
            self.cache_index['last_cleanup'] = current_time
            self._save_cache_index()
            
            final_size = self._calculate_cache_size()
            self.logger.info(f"缓存清理完成: {final_size / 1024 / 1024:.1f}MB")
    
    def _calculate_cache_size(self) -> int:
        """计算当前缓存总大小"""
        total_size = 0
        for category, items in self.cache_index.items():
            if category in ['parsed_docs', 'matches', 'content', 'quality_assessments']:
                for info in items.values():
                    total_size += info.get('size', 0)
        return total_size
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = {
            'total_size_mb': self._calculate_cache_size() / 1024 / 1024,
            'max_size_mb': self.max_cache_size_bytes / 1024 / 1024,
            'categories': {}
        }
        
        for category, items in self.cache_index.items():
            if category in ['parsed_docs', 'matches', 'content', 'quality_assessments']:
                category_size = sum(info.get('size', 0) for info in items.values())
                stats['categories'][category] = {
                    'count': len(items),
                    'size_mb': category_size / 1024 / 1024
                }
        
        return stats
    
    def clear_all_cache(self):
        """清空所有缓存"""
        with self._lock:
            try:
                # 删除所有缓存文件
                for cache_dir in [self.parsed_docs_dir, self.matches_dir, self.content_dir, self.quality_dir]:
                    for file_path in cache_dir.glob('*'):
                        if file_path.is_file():
                            file_path.unlink()
                
                # 重置索引
                self.cache_index = {
                    'parsed_docs': {},
                    'matches': {},
                    'content': {},
                    'quality_assessments': {},
                    'last_cleanup': time.time()
                }
                
                self._save_cache_index()
                self.logger.info("所有缓存已清空")
                
            except Exception as e:
                self.logger.error(f"清空缓存失败: {e}")


# 全局缓存实例
_document_cache = None

def get_document_cache() -> DocumentCache:
    """获取全局文档缓存实例"""
    global _document_cache
    if _document_cache is None:
        _document_cache = DocumentCache()
    return _document_cache

def set_document_cache(cache: DocumentCache):
    """设置全局文档缓存实例"""
    global _document_cache
    _document_cache = cache