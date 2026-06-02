import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)

class StageStatus:
    """阶段状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StateManager:
    """状态管理器，负责记录和管理工作流执行状态"""
    
    def __init__(self, state_file: str = "workflow_state.json"):
        """
        初始化状态管理器
        
        Args:
            state_file: 状态文件路径，默认为当前目录下的 workflow_state.json
        """
        self.state_file = state_file
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """加载状态文件，如果不存在则创建新的状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"加载状态文件失败，将创建新状态: {e}")
                return self._create_empty_state()
        return self._create_empty_state()
    
    def _create_empty_state(self) -> Dict:
        """创建空的状态结构"""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "runs": []  # 记录每次运行的状态
        }
    
    def _save_state(self) -> None:
        """保存状态到文件"""
        self.state["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.error(f"保存状态文件失败: {e}")
    
    def create_new_run(self, story_ids: List[str]) -> str:
        """
        创建新的运行记录
        
        Args:
            story_ids: 本次运行的需求ID列表
        
        Returns:
            run_id: 本次运行的唯一标识
        """
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_run = {
            "run_id": run_id,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "status": StageStatus.RUNNING,
            "story_ids": story_ids,
            "stages": {
                "download": {
                    "status": StageStatus.PENDING,
                    "start_time": None,
                    "end_time": None,
                    "completed_stories": []
                },
                "process": {
                    "status": StageStatus.PENDING,
                    "start_time": None,
                    "end_time": None,
                    "completed_stories": []
                },
                "gpt": {
                    "status": StageStatus.PENDING,
                    "start_time": None,
                    "end_time": None,
                    "completed_stories": []
                },
                "submit": {
                    "status": StageStatus.PENDING,
                    "start_time": None,
                    "end_time": None,
                    "completed_stories": []
                }
            },
            "errors": []
        }
        self.state["runs"].insert(0, new_run)
        self._save_state()
        logger.info(f"创建新的运行记录: {run_id}")
        return run_id
    
    def update_stage_status(self, run_id: str, stage_name: str, status: str, 
                           completed_stories: List[str] = None) -> None:
        """
        更新阶段状态
        
        Args:
            run_id: 运行ID
            stage_name: 阶段名称
            status: 阶段状态
            completed_stories: 已完成的需求ID列表
        """
        run = self._get_run(run_id)
        if not run:
            logger.error(f"未找到运行记录: {run_id}")
            return
        
        if stage_name not in run["stages"]:
            logger.error(f"未知阶段: {stage_name}")
            return
        
        now = datetime.now().isoformat()
        run["stages"][stage_name]["status"] = status
        
        if status == StageStatus.RUNNING:
            run["stages"][stage_name]["start_time"] = now
        elif status in [StageStatus.COMPLETED, StageStatus.FAILED]:
            run["stages"][stage_name]["end_time"] = now
        
        if completed_stories:
            run["stages"][stage_name]["completed_stories"].extend(completed_stories)
        
        self._save_state()
        logger.info(f"更新阶段状态: {run_id} -> {stage_name} = {status}")
    
    def update_story_status(self, run_id: str, stage_name: str, story_id: str, 
                           status: str) -> None:
        """
        更新单个需求在指定阶段的状态
        
        Args:
            run_id: 运行ID
            stage_name: 阶段名称
            story_id: 需求ID
            status: 状态
        """
        run = self._get_run(run_id)
        if not run:
            logger.error(f"未找到运行记录: {run_id}")
            return
        
        if stage_name not in run["stages"]:
            logger.error(f"未知阶段: {stage_name}")
            return
        
        if status == StageStatus.COMPLETED and story_id not in run["stages"][stage_name]["completed_stories"]:
            run["stages"][stage_name]["completed_stories"].append(story_id)
        
        self._save_state()
        logger.debug(f"更新需求状态: {run_id} -> {stage_name} -> {story_id} = {status}")
    
    def complete_run(self, run_id: str, success: bool = True) -> None:
        """
        完成运行记录
        
        Args:
            run_id: 运行ID
            success: 是否成功完成
        """
        run = self._get_run(run_id)
        if not run:
            logger.error(f"未找到运行记录: {run_id}")
            return
        
        run["end_time"] = datetime.now().isoformat()
        run["status"] = StageStatus.COMPLETED if success else StageStatus.FAILED
        self._save_state()
        logger.info(f"运行记录已完成: {run_id} (成功: {success})")
    
    def record_error(self, run_id: str, stage_name: str, story_id: str, error_msg: str) -> None:
        """
        记录错误信息
        
        Args:
            run_id: 运行ID
            stage_name: 阶段名称
            story_id: 需求ID
            error_msg: 错误信息
        """
        run = self._get_run(run_id)
        if not run:
            logger.error(f"未找到运行记录: {run_id}")
            return
        
        error_record = {
            "time": datetime.now().isoformat(),
            "stage": stage_name,
            "story_id": story_id,
            "error": error_msg
        }
        run["errors"].append(error_record)
        self._save_state()
        logger.error(f"记录错误: {run_id} -> {stage_name} -> {story_id}: {error_msg}")
    
    def get_completed_stories(self, stage_name: str = None) -> Set[str]:
        """
        获取已完成指定阶段的所有需求ID
        
        Args:
            stage_name: 阶段名称，如果为None则获取所有阶段都完成的需求
        
        Returns:
            已完成的需求ID集合
        """
        completed = set()
        
        for run in self.state["runs"]:
            if run["status"] != StageStatus.COMPLETED:
                continue
            
            if stage_name:
                if run["stages"].get(stage_name, {}).get("status") == StageStatus.COMPLETED:
                    completed.update(run["stages"][stage_name].get("completed_stories", []))
            else:
                # 获取所有阶段都完成的需求
                all_completed = set(run["story_ids"])
                for stage in run["stages"].values():
                    if stage["status"] == StageStatus.COMPLETED:
                        all_completed.intersection_update(stage.get("completed_stories", []))
                    else:
                        all_completed = set()
                        break
                completed.update(all_completed)
        
        return completed
    
    def check_story_completed(self, story_id: str, stage_name: str = "submit") -> bool:
        """
        检查需求是否已完成指定阶段
        
        Args:
            story_id: 需求ID
            stage_name: 阶段名称，默认为submit
        
        Returns:
            是否已完成
        """
        for run in self.state["runs"]:
            stage = run["stages"].get(stage_name)
            if stage and stage["status"] == StageStatus.COMPLETED:
                if story_id in stage.get("completed_stories", []):
                    return True
        return False
    
    def get_last_run(self) -> Optional[Dict]:
        """获取最近一次运行记录"""
        if self.state["runs"]:
            return self.state["runs"][0]
        return None
    
    def get_run(self, run_id: str) -> Optional[Dict]:
        """获取指定运行记录"""
        return self._get_run(run_id)
    
    def _get_run(self, run_id: str) -> Optional[Dict]:
        """内部方法：获取指定运行记录"""
        for run in self.state["runs"]:
            if run["run_id"] == run_id:
                return run
        return None
    
    def get_pending_stages(self, run_id: str) -> List[str]:
        """
        获取待执行的阶段列表（支持断点续跑）
        
        Args:
            run_id: 运行ID
        
        Returns:
            待执行的阶段名称列表
        """
        run = self._get_run(run_id)
        if not run:
            return []
        
        stages_order = ['download', 'process', 'gpt', 'submit']
        pending_stages = []
        
        for stage_name in stages_order:
            status = run["stages"].get(stage_name, {}).get("status")
            if status != StageStatus.COMPLETED:
                pending_stages.append(stage_name)
        
        return pending_stages
    
    def get_completed_stages(self, run_id: str) -> List[str]:
        """
        获取已完成的阶段列表
        
        Args:
            run_id: 运行ID
        
        Returns:
            已完成的阶段名称列表
        """
        run = self._get_run(run_id)
        if not run:
            return []
        
        completed_stages = []
        for stage_name, stage_data in run["stages"].items():
            if stage_data.get("status") == StageStatus.COMPLETED:
                completed_stages.append(stage_name)
        
        return completed_stages
    
    def reset_run(self, run_id: str) -> None:
        """
        重置运行记录（将所有阶段状态设为pending）
        
        Args:
            run_id: 运行ID
        """
        run = self._get_run(run_id)
        if not run:
            logger.error(f"未找到运行记录: {run_id}")
            return
        
        for stage_name in run["stages"]:
            run["stages"][stage_name] = {
                "status": StageStatus.PENDING,
                "start_time": None,
                "end_time": None,
                "completed_stories": []
            }
        
        run["status"] = StageStatus.PENDING
        run["end_time"] = None
        run["errors"] = []
        
        self._save_state()
        logger.info(f"已重置运行记录: {run_id}")
    
    def clear_old_runs(self, days_to_keep: int = 30) -> None:
        """
        清理旧的运行记录
        
        Args:
            days_to_keep: 保留天数，默认为30天
        """
        cutoff_time = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_time.isoformat()
        
        original_count = len(self.state["runs"])
        self.state["runs"] = [
            run for run in self.state["runs"]
            if run["start_time"] > cutoff_str
        ]
        
        removed_count = original_count - len(self.state["runs"])
        if removed_count > 0:
            self._save_state()
            logger.info(f"清理了 {removed_count} 条旧的运行记录")
    
    def print_status(self, run_id: str = None) -> None:
        """
        打印运行状态
        
        Args:
            run_id: 运行ID，如果为None则打印最近一次运行的状态
        """
        if run_id:
            run = self._get_run(run_id)
        else:
            run = self.get_last_run()
        
        if not run:
            logger.info("没有找到运行记录")
            return
        
        print(f"\n========== 运行状态 [{run['run_id']}] ==========")
        print(f"开始时间: {run['start_time']}")
        print(f"结束时间: {run['end_time'] or '运行中'}")
        print(f"总体状态: {run['status']}")
        print(f"需求列表: {', '.join(run['story_ids'])}")
        
        print("\n各阶段状态:")
        for stage_name, stage_data in run["stages"].items():
            status = stage_data["status"]
            completed = len(stage_data.get("completed_stories", []))
            print(f"  {stage_name}: {status} (已完成 {completed} 个需求)")
        
        if run["errors"]:
            print("\n错误记录:")
            for error in run["errors"]:
                print(f"  [{error['time']}] {error['stage']} -> {error['story_id']}: {error['error']}")
        
        print("=" * 50)


# 全局状态管理器实例
state_manager = StateManager()