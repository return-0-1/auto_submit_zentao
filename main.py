import argparse
import logging
from workflow import WorkflowManager
from workflow.state_manager import state_manager
from utils.log_utils import setup_logging, log_level_from_string


def main():
    """禅道自动化工具统一入口"""
    parser = argparse.ArgumentParser(description='禅道自动化工具')
    
    # 全局日志参数
    parser.add_argument('-v', '--verbose', action='count', default=0, 
                        help='增加日志详细程度，-v 为 DEBUG，默认 INFO')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO', help='设置日志级别')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    subparsers.add_parser('download', help='下载需求文件')
    subparsers.add_parser('process', help='处理需求文件')
    subparsers.add_parser('gpt', help='GPT处理')
    subparsers.add_parser('submit', help='提交测试用例/缺陷')
    
    run_parser = subparsers.add_parser('run', help='执行完整流程：下载→处理→GPT→提交')
    run_parser.add_argument('--clean', action='store_true', help='流程执行完成后自动清理所有临时文件')
    run_parser.add_argument('--clean-stages', nargs='+', choices=['download', 'process', 'gpt', 'all'], 
                           help='指定要清理的阶段文件')
    run_parser.add_argument('--resume', action='store_true', help='从断点续跑')
    run_parser.add_argument('--no-skip', action='store_true', help='不跳过已完成的需求，强制重新执行')
    
    clean_parser = subparsers.add_parser('clean', help='清理各阶段产生的临时文件')
    clean_parser.add_argument('stages', nargs='*', 
                             choices=['download', 'process', 'gpt', 'all'],
                             help='要清理的阶段，默认为清理所有')
    
    status_parser = subparsers.add_parser('status', help='查看运行状态和已完成的需求')
    status_parser.add_argument('--stage', choices=['download', 'process', 'gpt', 'submit'], 
                              default='submit', help='指定要查看的阶段，默认为submit')
    
    subparsers.add_parser('reset-state', help='重置所有运行状态记录')

    args = parser.parse_args()
    
    # 配置日志
    # 优先使用 --log-level 参数，其次使用 -v 参数
    if args.log_level:
        log_level = log_level_from_string(args.log_level)
    elif args.verbose >= 1:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    setup_logging(log_level=log_level)

    if not args.command:
        parser.print_help()
        return

    wf = WorkflowManager()

    try:
        if args.command == 'download':
            wf.run_stage('download')
        elif args.command == 'process':
            wf.run_stage('process')
        elif args.command == 'gpt':
            wf.run_stage('gpt')
        elif args.command == 'submit':
            wf.run_stage('submit')
        elif args.command == 'run':
            wf.run_full_pipeline(resume=args.resume, skip_completed=not args.no_skip)
            
            if args.clean:
                logging.info("开始清理临时文件...")
                wf.clean_files(['all'])
            elif args.clean_stages:
                logging.info(f"开始清理指定阶段的文件: {args.clean_stages}")
                wf.clean_files(args.clean_stages)
        elif args.command == 'clean':
            wf.clean_files(args.stages if args.stages else ['all'])
        elif args.command == 'status':
            completed = wf.check_completed_stories(args.stage)
            print(f"\n已完成 '{args.stage}' 阶段的需求:")
            if completed:
                for story_id in completed:
                    print(f"  ✓ {story_id}")
            else:
                print("  暂无已完成的需求")
            print(f"\n共 {len(completed)} 个需求已完成")
        elif args.command == 'reset-state':
            import os
            import sys
            
            # 获取应用程序根目录
            if getattr(sys, 'frozen', False):
                app_root = os.path.dirname(sys.executable)
            else:
                app_root = os.path.dirname(os.path.abspath(__file__))
            
            state_file = os.path.join(app_root, "workflow_state.json")
            if os.path.exists(state_file):
                os.remove(state_file)
                logging.info(f"状态文件已重置: {state_file}")
            else:
                logging.info(f"状态文件不存在: {state_file}")
        
        if args.command not in ['status', 'reset-state']:
            logging.info(f"命令 '{args.command}' 执行完成")
    except Exception as e:
        logging.error(f"命令 '{args.command}' 执行失败: {e}")
        raise


if __name__ == "__main__":
    main()
