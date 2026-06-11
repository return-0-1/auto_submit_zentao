# Custom hook to override third-party workflow hook
# This hook ensures our project's workflow module is imported correctly

hiddenimports = [
    'workflow',
    'workflow.download_stage',
    'workflow.gpt_stage',
    'workflow.process_stage',
    'workflow.state_manager',
    'workflow.submit_stage',
    'workflow.workflow_manager',
]

# 排除第三方 workflow 模块
excludedimports = ['workflow']
