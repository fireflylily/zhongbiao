#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历批量导出处理器
支持选择多个人员，导出简历和相关附件（身份证、学历证书、资质证书等）
"""

import os
import zipfile
import json
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .manager import ResumeLibraryManager


class ResumeExportHandler:
    """简历批量导出处理器"""

    def __init__(self, db_path: str = None):
        """
        初始化导出处理器
        Args:
            db_path: 数据库路径
        """
        self.manager = ResumeLibraryManager(db_path)
        self.temp_dir = Path('data/temp')
        self.export_dir = Path('data/exports')

        # 确保目录存在
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_resumes(self,
                       resume_ids: List[int],
                       export_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        批量导出简历和附件
        Args:
            resume_ids: 要导出的简历ID列表
            export_options: 导出选项
                - include_attachments: 是否包含附件（默认True）
                - attachment_categories: 要导出的附件类别列表
                - format: 导出格式（'zip'或'folder'）
                - include_summary: 是否包含汇总文件（默认True）
                - organize_by_category: 是否按类别组织文件（默认True）
        Returns:
            导出结果信息
        """
        if not resume_ids:
            raise ValueError("请选择要导出的简历")

        # 默认选项
        options = {
            'include_attachments': True,
            'attachment_categories': ['resume', 'id_card', 'education', 'degree',
                                     'qualification', 'award'],
            'format': 'zip',
            'include_summary': True,
            'organize_by_category': True
        }
        if export_options:
            options.update(export_options)

        # 创建临时导出目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_name = f"resume_export_{timestamp}"
        temp_export_path = self.temp_dir / export_name

        try:
            # 创建导出目录结构
            self._create_export_structure(temp_export_path, options)

            # 导出每个简历
            export_stats = {
                'total_resumes': 0,
                'total_attachments': 0,
                'exported_files': [],
                'errors': []
            }

            for resume_id in resume_ids:
                try:
                    self._export_single_resume(
                        resume_id,
                        temp_export_path,
                        options,
                        export_stats
                    )
                    export_stats['total_resumes'] += 1
                except Exception as e:
                    export_stats['errors'].append({
                        'resume_id': resume_id,
                        'error': str(e)
                    })

            # 生成汇总文件
            if options['include_summary']:
                self._generate_summary(temp_export_path, resume_ids, export_stats)

            # 打包或返回文件夹路径
            if options['format'] == 'zip':
                zip_path = self._create_zip_archive(temp_export_path, export_name)
                # 清理临时文件夹
                shutil.rmtree(temp_export_path)
                return {
                    'success': True,
                    'format': 'zip',
                    'file_path': str(zip_path),
                    'file_name': f"{export_name}.zip",
                    'stats': export_stats
                }
            else:
                # 移动到导出目录
                final_path = self.export_dir / export_name
                if final_path.exists():
                    shutil.rmtree(final_path)
                shutil.move(str(temp_export_path), str(final_path))
                return {
                    'success': True,
                    'format': 'folder',
                    'folder_path': str(final_path),
                    'stats': export_stats
                }

        except Exception as e:
            # 清理临时文件
            if temp_export_path.exists():
                shutil.rmtree(temp_export_path)
            raise Exception(f"导出失败: {str(e)}")

    def _create_export_structure(self, base_path: Path, options: Dict[str, Any]):
        """
        创建导出目录结构
        Args:
            base_path: 基础路径
            options: 导出选项
        """
        base_path.mkdir(parents=True, exist_ok=True)

        if options['organize_by_category'] and options['include_attachments']:
            # 按类别创建子目录
            categories = {
                'resume': '简历文件',
                'id_card': '身份证',
                'education': '学历证书',
                'degree': '学位证书',
                'qualification': '资质证书',
                'award': '获奖证书',
                'other': '其他材料'
            }

            for category_key, category_name in categories.items():
                if category_key in options['attachment_categories']:
                    (base_path / category_name).mkdir(exist_ok=True)

        # 创建简历信息目录
        (base_path / '人员信息').mkdir(exist_ok=True)

    def _export_single_resume(self,
                             resume_id: int,
                             export_path: Path,
                             options: Dict[str, Any],
                             stats: Dict[str, Any]):
        """
        导出单个简历
        Args:
            resume_id: 简历ID
            export_path: 导出路径
            options: 导出选项
            stats: 统计信息
        """
        # 获取简历信息
        resume = self.manager.get_resume_by_id(resume_id)
        if not resume:
            raise ValueError(f"简历不存在: {resume_id}")

        # 导出简历基本信息为JSON文件
        info_file = export_path / '人员信息' / f"{resume['name']}_信息.json"
        self._export_resume_info(resume, info_file)
        stats['exported_files'].append(str(info_file))

        # 导出附件
        if options['include_attachments'] and resume.get('attachments'):
            for attachment in resume['attachments']:
                if attachment['attachment_category'] in options['attachment_categories']:
                    self._export_attachment(
                        attachment,
                        resume['name'],
                        export_path,
                        options,
                        stats
                    )

    def _export_resume_info(self, resume: Dict[str, Any], file_path: Path):
        """
        导出简历信息为JSON文件
        Args:
            resume: 简历数据
            file_path: 文件路径
        """
        # 移除系统字段
        export_data = {k: v for k, v in resume.items()
                      if k not in ['resume_id', 'created_at', 'updated_at', 'attachments']}

        # 格式化输出
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

    def _export_attachment(self,
                          attachment: Dict[str, Any],
                          person_name: str,
                          export_path: Path,
                          options: Dict[str, Any],
                          stats: Dict[str, Any]):
        """
        导出单个附件
        Args:
            attachment: 附件信息
            person_name: 人员姓名
            export_path: 导出路径
            options: 导出选项
            stats: 统计信息
        """
        source_path = Path(attachment['file_path'])
        if not source_path.exists():
            print(f"附件文件不存在: {source_path}")
            return

        # 确定目标路径
        if options['organize_by_category']:
            category_map = {
                'resume': '简历文件',
                'id_card': '身份证',
                'education': '学历证书',
                'degree': '学位证书',
                'qualification': '资质证书',
                'award': '获奖证书',
                'other': '其他材料'
            }
            category_folder = category_map.get(attachment['attachment_category'], '其他材料')
            target_dir = export_path / category_folder
        else:
            target_dir = export_path

        # 生成目标文件名（包含人员姓名）
        file_ext = Path(attachment['original_filename']).suffix
        target_name = f"{person_name}_{attachment['attachment_category']}{file_ext}"

        # 处理重名文件
        target_file = target_dir / target_name
        counter = 1
        while target_file.exists():
            target_name = f"{person_name}_{attachment['attachment_category']}_{counter}{file_ext}"
            target_file = target_dir / target_name
            counter += 1

        # 复制文件
        shutil.copy2(source_path, target_file)
        stats['total_attachments'] += 1
        stats['exported_files'].append(str(target_file))

    def _generate_summary(self,
                         export_path: Path,
                         resume_ids: List[int],
                         stats: Dict[str, Any]):
        """
        生成导出汇总文件
        Args:
            export_path: 导出路径
            resume_ids: 简历ID列表
            stats: 统计信息
        """
        summary_data = {
            '导出时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '导出数量': {
                '简历数量': stats['total_resumes'],
                '附件数量': stats['total_attachments'],
                '文件总数': len(stats['exported_files'])
            },
            '人员列表': []
        }

        # 获取每个人员的基本信息
        for resume_id in resume_ids:
            try:
                resume = self.manager.get_resume_by_id(resume_id)
                if resume:
                    person_info = {
                        '姓名': resume.get('name', ''),
                        '性别': resume.get('gender', ''),
                        '学历': resume.get('education_level', ''),
                        '职位': resume.get('current_position', ''),
                        '单位': resume.get('current_company', ''),
                        '电话': resume.get('phone', ''),
                        '邮箱': resume.get('email', ''),
                        '附件数量': len(resume.get('attachments', []))
                    }
                    summary_data['人员列表'].append(person_info)
            except:
                continue

        # 添加错误信息
        if stats['errors']:
            summary_data['导出错误'] = stats['errors']

        # 生成汇总文件
        summary_file = export_path / '导出汇总.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

        # 生成人员清单（Excel格式的CSV）
        self._generate_person_list_csv(export_path, summary_data['人员列表'])

    def _generate_person_list_csv(self, export_path: Path, person_list: List[Dict[str, Any]]):
        """
        生成人员清单CSV文件
        Args:
            export_path: 导出路径
            person_list: 人员列表
        """
        if not person_list:
            return

        csv_file = export_path / '人员清单.csv'

        # CSV头部（添加BOM以支持Excel正确显示中文）
        with open(csv_file, 'wb') as f:
            f.write(b'\xef\xbb\xbf')  # UTF-8 BOM

        with open(csv_file, 'a', encoding='utf-8') as f:
            # 写入表头
            headers = ['序号', '姓名', '性别', '学历', '职位', '单位', '电话', '邮箱', '附件数量']
            f.write(','.join(headers) + '\n')

            # 写入数据
            for idx, person in enumerate(person_list, 1):
                row = [
                    str(idx),
                    person.get('姓名', ''),
                    person.get('性别', ''),
                    person.get('学历', ''),
                    person.get('职位', ''),
                    person.get('单位', ''),
                    person.get('电话', ''),
                    person.get('邮箱', ''),
                    str(person.get('附件数量', 0))
                ]
                # 处理包含逗号的字段
                row = [f'"{field}"' if ',' in field else field for field in row]
                f.write(','.join(row) + '\n')

    def _create_zip_archive(self, source_path: Path, archive_name: str) -> Path:
        """
        创建ZIP压缩包
        Args:
            source_path: 源文件夹路径
            archive_name: 压缩包名称
        Returns:
            压缩包路径
        """
        zip_path = self.export_dir / f"{archive_name}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    # 计算相对路径
                    arcname = file_path.relative_to(source_path)
                    zipf.write(file_path, arcname)

        return zip_path

    def export_single_resume_pdf(self, resume_id: int) -> Dict[str, Any]:
        """
        导出单个简历为PDF格式（预留接口）
        Args:
            resume_id: 简历ID
        Returns:
            导出结果
        """
        # TODO: 实现简历PDF生成功能
        # 可以使用reportlab或weasyprint等库生成PDF
        raise NotImplementedError("PDF导出功能待实现")

    def get_export_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取导出历史
        Args:
            limit: 返回数量限制
        Returns:
            导出历史列表
        """
        export_files = []

        # 扫描导出目录
        for file_path in self.export_dir.iterdir():
            if file_path.suffix == '.zip':
                stat = file_path.stat()
                export_files.append({
                    'filename': file_path.name,
                    'filepath': str(file_path),
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        # 按创建时间倒序排序
        export_files.sort(key=lambda x: x['created_at'], reverse=True)

        return export_files[:limit]

    def cleanup_old_exports(self, days: int = 7):
        """
        清理旧的导出文件
        Args:
            days: 保留天数
        """
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)

        for file_path in self.export_dir.iterdir():
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                except:
                    pass