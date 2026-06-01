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

    def run_stage(self, stage_name: str):
        """运行单个阶段"""
        stage = self.stages.get(stage_name)
        if stage:
            logging.info(f"开始执行阶段: {stage_name}")
            stage.execute()
            logging.info(f"阶段 {stage_name} 执行完成")
        else:
            logging.error(f"未知阶段: {stage_name}")
            raise ValueError(f"未知阶段: {stage_name}")

    def run_full_pipeline(self):
        """运行完整流程：下载 → 处理 → GPT → 提交"""
        stages_order = ['download', 'process', 'gpt', 'submit']
        
        logging.info("开始执行完整流程")
        for stage_name in stages_order:
            try:
                self.run_stage(stage_name)
            except Exception as e:
                logging.error(f"阶段 {stage_name} 执行失败: {e}")
                raise
        logging.info("完整流程执行完成")
