langs = {
    'zh-CN': {
        'init.user.intro': '检查到你是第一次使用本工具，请提供一些初始化信息',
        'init.user.lang': '请选择要使用的语言：[1]中文，[2]English',

        'args.log': '查看记录',
        'args.commit': '提交补丁',
        'args.init': '初始化当前目录为工作空间',
        'args.usage': '各个参数的使用方法',

        'args.prepare': '为提补丁做准备，包括：更新当前分支代码、丢弃本地所有修改，使其与远程保持一致',
        'args.not_git': '当前目录不是有效的Linux的GIT仓库，请在GIT仓库执行本脚本',
        'args.clone': '克隆指定提交',
        'args.continue': '继续之前的提交',
        'args.new': '为指定提交创建一个新版本',
        'args.restore': '恢复指定提交到当前内核仓库，加参数--no-content会只恢复log记录而丢弃具体的提交内容',
        'args.no-content': '指定该参数时，restore和clone都将丢弃具体的提交内容',
        'args.group': '指定要提交到的分组，同一个分组的提交会作为一个系列补丁，使用send -g <group>来进行发送',
        'args.send-group': '将指定分组的补丁作为系列补丁进行发送',

        'args.log.group': '查找特定分组的记录',
        'args.log.import': '将autopatch-export.json中的数据导入到当前仓库',
        'args.log.export': '将指定的提交数据导出到文件autopatch-export.json',
        'args.clear': '删除所有的log记录',
        'args.delete': '删除指定的提交记录',
        'args.status': '手动为提交设置状态，与--key配合使用',
        'args.key': '提交的key值',
        'args.update': '查询远程分支以更新所有提交状态（是否被采纳）',
        'args.title': '修改提交标题',
        'args.no-add': '不进行git add操作，直接commit',
        'args.open': '将提交的状态改为re_commit',

        'args.send': '进行补丁的发送',

        'git.invalid_branch': '当前未处于有效分支！',
        'work.init': '当前目录非AutoPatch工作空间，是否将其初始化为工作空间？',
        'work.select_kernel': '请设置内核代码根路径',
        'commit.no_continue': '没有找到可继续的提交',
        'commit.test_email': '测试邮箱',
        'commit.test_email_info': '请提供您的测试邮箱',
        'commit.select_mt': '下面将进行补丁的邮件发送，请选择补丁的收件人（其余的将被抄送）',
        'commit.no_to': '未选择收件人，已停止！',
        'commit.send_target': '请选择补丁发送的目的地',
        'commit.to_kernel': '发送到开源社区',
        'commit.to_test': '发送到测试邮箱',
        'commit.checkpatch_err': '补丁存在格式错误，请进行修复，修复完成后运行autopatch.py --continue来进行提交。'
                                 '格式错误信息如下：',
        'commit.review': '是否要预览补丁？',
        'commit.no_commit': '提交信息不完整，已停止！',
        'commit.commit': '下面的修改将被提交：',
        'commit.confirm': '确认提交？y/n[y]:',
        'commit.select_to': '请选择收件人',
        'commit.no_mt': '找不到维护者，已停止！',
        'commit.checkpatch_ok': '补丁无格式问题，可以放心发送啦！',
        'commit.version': '''# 当前补丁版本为：{version}，请将版本变更信息写到末尾，
# 常用的版本变更格式如下：
# Signed-off-by: xxx
# ---
# v3:
# - some change info
# - some change info
# v2:
# - some change info
''',
        'commit.not_found': '找不到该提交！',
        'commit.restore_err': '恢复提交异常！',
        'commit.select_cc': '请选择补丁抄送人',
        'commit.no_cc': '未选择抄送人，已停止！',
        'commit.select_template': '请选择要使用的模板Select the template you want to use',
        'commit.wait': '请稍等......',
        'commit.new_group': '找不到组，这将是一个新组',
        'commit.new_mt': '新增收件人',
        'dialog.button_new': '新增',
        'dialog.button_ignore': '忽略',
        'dialog.button_cancel': '取消',
        'git.invalid_remote': '当前分支没有绑定远程分支！'
    },
    'en': {
        'init.user.intro': 'Check that you are using this tool for the first time, please provide some initialization '
                           'information',
        'init.user.lang': 'Please select the language you want to use: [1] Chinese, [2] English',

        'args.log': 'View log',
        'args.commit': 'Submit patch',
        'args.init': 'Initialize the current directory as a workspace',
        'args.usage': 'How to use each parameter',

        'args.prepare': 'Prepare for the patch, including: update the current branch code, discard all local changes, '
                        'and make it consistent with the remote',
        'args.not_git': 'The current directory is not a valid Linux GIT repository, please execute this script in the '
                        'GIT repository',
        'args.clone': 'Clone specified commit',
        'args.continue': 'Continue the previous submission',
        'args.new': 'Create a new version for the specified submission',
        'args.restore': 'Restore the specified submission to the current kernel warehouse, adding the parameter '
                        '--no-content will only restore the log record and discard the specific submission content',
        'args.no-content': 'When this parameter is specified, both restore and clone will discard the specific '
                           'submission content',
        'args.group': 'Specify the group to be submitted to, the submission of the same group will be used as a '
                      'series of patches, use --send-group to send',
        'args.send-group': 'Send the patch of the specified group as a series of patches',

        'args.log.group': 'Find records in a specific group',
        'args.log.import': 'import commit from autopatch-export.json',
        'args.log.export': 'export commit to autopatch-export.json',
        'args.clear': 'Delete all log records',
        'args.delete': 'Delete the specified submission record',
        'args.status': 'Manually set the status for submission, used in conjunction with --key',
        'args.key': 'Submitted key value',
        'args.update': 'Query the remote branch has updated all submission status (whether it has been adopted)',
        'args.title': 'change commit title',
        'args.no-add': 'not git add',
        'args.open': 'change a log\'s status to re_commit',

        'args.send': 'send the patches',

        'git.invalid_branch': 'Currently not in a valid branch! ',
        'work.init': 'The current directory is not an AutoPatch workspace. Should it be initialized as a workspace? ',
        'work.select_kernel': 'Please set the kernel code root path',
        'commit.no_continue': 'No commit to continue was found',
        'commit.test_email': 'Test Email',
        'commit.test_email_info': 'Please provide your test email',
        'commit.select_mt': 'The patch will be sent by mail below, please select the recipient of the patch (the rest '
                            'will be copied)',
        'commit.no_to': 'No recipient selected, stopped! ',
        'commit.send_target': 'Please select the destination of the patch',
        'commit.to_kernel': 'Send to open source community',
        'commit.to_test': 'Send to test mailbox',
        'commit.checkpatch_err': 'The patch has a format error, please fix it. After the repair is complete, '
                                 'run autopatch.py ​​--continue to submit it. '
                                 'The format error message is as follows:',
        'commit.review': 'Do you want to preview the patch? ',
        'commit.no_commit': 'The submission information is incomplete and has been stopped! ',
        'commit.commit': 'The following changes will be submitted:',
        'commit.confirm': 'Confirm to submit? y/n[y]:',
        'commit.select_to': 'Please select the recipient',
        'commit.no_mt': 'Cannot find maintainer, stopped! ',
        'commit.checkpatch_ok': 'The patch has no format problem, you can send it with confidence! ',
        'commit.version': '''# The current patch version is: {version}, please write the version
# change information to the end.
# The commonly used version change format is as follows:
# Signed-off-by: xxx
# ---
# v3:
# -some change info
# -some change info
# v2:
# -some change info''',
        'commit.not_found': 'commit not found!',
        'commit.restore_err': 'Recover submission exception!',
        'commit.select_cc': 'please choose cc',
        'commit.no_cc': 'Cc not selected, stopped!',
        'commit.select_template': 'Select the template you want to use',
        'commit.wait': 'Please wait a moment......',
        'commit.new_group': 'Group not found and this will be a new group',
        'commit.new_mt': 'Add recipient',
        'dialog.button_new': 'NEW',
        'dialog.button_ignore': 'IGNORE',
        'dialog.button_cancel': 'CANCEL',
        'git.invalid_remote': 'current branch has no upstream!'
    }
}

cur_lang = 'zh-CN'


def set_lang(lang):
    global cur_lang
    cur_lang = lang


def get_lang():
    return cur_lang


def get_text(key: str):
    return langs[cur_lang][key]


_ = get_text
