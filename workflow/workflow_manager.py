import logging
import os
import shutil
from typing import List
from config.constants import DEBUG_MODE, DOWNLOAD_FOLDER, OUTPUT_BASE_FOLDER, JSON_DATA_PATH, DEFAULT_STORY_ID_LIST, USERNAME, PASSWORD
from workflow.state_manager import state_manager, StageStatus
from core.business_handler import BusinessHandler


class WorkflowManager:
    """工作流管理器，负责编排和执行各个阶段"""

    def __init__(self):
        from workflow.download_stage import DownloadStage
        from workflow.submit_stage import SubmitStage
        from workflow.process_stage import ProcessStage
        from workflow.gpt_stage import GptStage
        
        self.stages = {
            'download': DownloadStage(),
            'process': ProcessStage(),
            'gpt': GptStage(),
            'submit': SubmitStage()
        }
        
        self.current_run_id = None
        self.story_ids = DEFAULT_STORY_ID_LIST
        
        # 共享的业务处理器（实现单例登录）
        self.handler = None
        
        if DEBUG_MODE:
            logging.info("[调试模式] 已启用，表单提交操作将仅输出日志，不真正提交")

    def clean_files(self, stages: list = None) -> None:
        """
        清理各阶段产生的文件
        
        Args:
            stages: 需要清理的阶段列表，可选值: ['download', 'process', 'gpt', 'all']
                    如果为 None 或 'all'，则清理所有阶段的文件
        """
        if stages is None or stages == ['all'] or 'all' in stages:
            folders_to_clean = [DOWNLOAD_FOLDER, OUTPUT_BASE_FOLDER, JSON_DATA_PATH]
        else:
            folders_to_clean = []
            if 'download' in stages:
                folders_to_clean.append(DOWNLOAD_FOLDER)
            if 'process' in stages:
                folders_to_clean.append(OUTPUT_BASE_FOLDER)
            if 'gpt' in stages:
                folders_to_clean.append(JSON_DATA_PATH)
        
        for folder in folders_to_clean:
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                    logging.info(f"已清理文件夹: {folder}")
                except Exception as e:
                    logging.error(f"清理文件夹失败 {folder}: {e}")
            else:
                logging.info(f"文件夹不存在，跳过清理: {folder}")

    def _init_handler(self):
        """初始化共享的业务处理器（只初始化一次）"""
        if not self.handler:
            self.handler = BusinessHandler(USERNAME, PASSWORD)
            logging.info("已初始化共享业务处理器")
    
    def run_stage(self, stage_name: str, story_ids: List[str] = None):
        """
        运行单个阶段
        
        Args:
            stage_name: 阶段名称
            story_ids: 需求ID列表，如果为None则使用默认列表
        """
        stage = self.stages.get(stage_name)
        if not stage:
            logging.error(f"未知阶段: {stage_name}")
            raise ValueError(f"未知阶段: {stage_name}")
        
        target_story_ids = story_ids or self.story_ids
        
        # 检查已完成的需求
        completed_stories = state_manager.get_completed_stories(stage_name)
        pending_stories = [s for s in target_story_ids if s not in completed_stories]
        
        if not pending_stories:
            logging.info(f"阶段 {stage_name} 所有需求已完成，跳过")
            if self.current_run_id:
                state_manager.update_stage_status(self.current_run_id, stage_name, StageStatus.COMPLETED, target_story_ids)
            return
        
        logging.info(f"开始执行阶段: {stage_name}")
        logging.info(f"待处理需求: {pending_stories}")
        
        # 更新状态为运行中
        if self.current_run_id:
            state_manager.update_stage_status(self.current_run_id, stage_name, StageStatus.RUNNING)
        
        try:
            # 对于需要登录的阶段，先初始化handler
            if stage_name in ['download', 'submit']:
                self._init_handler()
            
            # 执行阶段（传递handler）
            stage.execute(story_ids=pending_stories, handler=self.handler)
            
            # 更新状态为已完成
            if self.current_run_id:
                state_manager.update_stage_status(self.current_run_id, stage_name, StageStatus.COMPLETED, target_story_ids)
            
            logging.info(f"阶段 {stage_name} 执行完成")
            
        except Exception as e:
            # 更新状态为失败
            if self.current_run_id:
                state_manager.update_stage_status(self.current_run_id, stage_name, StageStatus.FAILED)
                for story_id in pending_stories:
                    state_manager.record_error(self.current_run_id, stage_name, story_id, str(e))
            
            logging.error(f"阶段 {stage_name} 执行失败: {e}")
            raise

    def run_full_pipeline(self, story_ids: List[str] = None, resume: bool = False, skip_completed: bool = True):
        """
        运行完整流程：下载 → 处理 → GPT → 提交
        
        Args:
            story_ids: 需求ID列表，如果为None则使用默认列表
            resume: 是否从断点续跑
            skip_completed: 是否跳过已完成的需求
        """
        stages_order = ['download', 'process', 'gpt', 'submit']
        self.story_ids = story_ids or DEFAULT_STORY_ID_LIST
        
        logging.info("开始执行完整流程")
        if DEBUG_MODE:
            logging.info("[调试模式] 流程执行中，所有提交操作将被跳过")
        
        # 检查已完成提交的需求
        if skip_completed:
            completed_submit = state_manager.get_completed_stories('submit')
            new_story_ids = [s for s in self.story_ids if s not in completed_submit]
            
            if new_story_ids != self.story_ids:
                completed_count = len(self.story_ids) - len(new_story_ids)
                logging.info(f"检测到 {completed_count} 个需求已完成提交，将跳过这些需求")
                logging.info(f"已完成的需求: {set(self.story_ids) - set(new_story_ids)}")
                self.story_ids = new_story_ids
            
            if not self.story_ids:
                logging.info("所有需求都已完成提交，流程结束")
                return
        
        # 创建新的运行记录
        self.current_run_id = state_manager.create_new_run(self.story_ids)
        
        try:
            for stage_name in stages_order:
                if resume:
                    # 检查阶段是否已完成
                    run = state_manager.get_run(self.current_run_id)
                    if run and run["stages"].get(stage_name, {}).get("status") == StageStatus.COMPLETED:
                        logging.info(f"阶段 {stage_name} 已完成，跳过")
                        continue
                
                self.run_stage(stage_name)
            
            state_manager.complete_run(self.current_run_id, success=True)
            logging.info("完整流程执行完成")
            
        except Exception as e:
            state_manager.complete_run(self.current_run_id, success=False)
            logging.error(f"完整流程执行失败: {e}")
            raise
        finally:
            # 流程结束时关闭handler
            if self.handler:
                self.handler.close()
                self.handler = None

    def check_completed_stories(self, stage_name: str = 'submit') -> List[str]:
        """
        检查已完成指定阶段的需求
        
        Args:
            stage_name: 阶段名称，默认为submit
        
        Returns:
            已完成的需求ID列表
        """
        return list(state_manager.get_completed_stories(stage_name))

    def show_status(self):
        """显示当前状态"""
        state_manager.print_status(self.current_run_id)