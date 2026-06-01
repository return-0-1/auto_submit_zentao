import argparse
import logging
from workflow import WorkflowManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    """禅道自动化工具统一入口"""
    parser = argparse.ArgumentParser(description='禅道自动化工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    subparsers.add_parser('download', help='下载需求文件')
    subparsers.add_parser('process', help='处理需求文件（待开发）')
    subparsers.add_parser('gpt', help='GPT处理（待开发）')
    subparsers.add_parser('submit', help='提交测试用例/缺陷')
    subparsers.add_parser('run', help='执行完整流程：下载→处理→GPT→提交')

    args = parser.parse_args()

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
            wf.run_full_pipeline()
        
        logging.info(f"命令 '{args.command}' 执行完成")
    except Exception as e:
        logging.error(f"命令 '{args.command}' 执行失败: {e}")
        raise


if __name__ == "__main__":
    main()
