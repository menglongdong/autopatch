#!/usr/bin/python3
import argparse

from config import *
from git import init_git
from langs import _
from machine import git, Commit, CommitMachine, init_commit


def show_logs(commits):
    print('%-12s %-20s %-20s %-8s %-8s %-6s %-10s %-20s' % (
        'key',
        'create date',
        'update date', 'version',
        'group', 'order', 'status', 'title',))

    for i in commits:
        print('%-12s %-20s %-20s v%-7s %-8s %-6s %-10s %-20s' % (
            i['key'],
            i['create'],
            i['update'], i['version'],
            i['group'], i['order'], i['status'], i['title']))


class PatchOps:
    """
    docstring
    """

    def __init__(self):
        self.args = None

    @staticmethod
    def dispatch(user_args, m):
        """
        docstring
        """
        ops = PatchOps()
        ops.args = user_args
        for (k, v) in user_args.__dict__.items():
            if v and k.startswith('do_'):
                ops_func = getattr(ops, k)
                if not ops_func:
                    continue
                ops_func()
                return

        def_ops = {
            'commit': ops.do_commit,
            'log': ops.do_log
        }
        def_ops[m]()

    @staticmethod
    def do_prepare():
        """
        docstring
        """
        git.git_dist_clean()

    def do_continue(self):
        commit = Commit.find_continue(git.get_last_title())
        if not commit:
            print(_('commit.no_continue'))
            exit(1)

        if len(commit) > 1:
            print('duplicated commit found!')
            exit(1)

        commit = commit[0]
        machine = CommitMachine(self.args)
        machine.set_start(commit['status'])
        machine.commit = commit
        machine.run()

    def do_new_version(self):
        key = self.args.do_new_version
        machine = CommitMachine(self.args)
        machine.set_start('new_version')
        machine.run(key)

    def do_commit(self):
        machine = CommitMachine(self.args)
        machine.run()

    def do_restore(self):
        key = self.args.do_restore
        commit = Commit.find_key(key)

        machine = CommitMachine(self.args)
        machine.set_start('restore')
        machine.commit = commit
        machine.run()

    @staticmethod
    def do_log():
        commits = Commit.get_commits()
        show_logs(commits)

    def do_log_group(self):
        group = self.args.do_log_group
        commits = Commit.find_group(group)
        show_logs(commits)

    @staticmethod
    def do_log_clear():
        Commit.get_commits().clear()
        Commit.store_commit()

    def change_log_attr(self, attr, val):
        if 'key' not in self.args.__dict__:
            print('key is necessary!')
            return

        commit = Commit.find_key(self.args.key)
        if not commit:
            print(_('commit.no_continue'))
            return

        commit[attr] = val
        Commit.store_commit()

    def do_change_status(self):
        status = self.args.do_change_status
        return self.change_log_attr('status', status)

    def do_change_title(self):
        title = self.args.do_change_title
        return self.change_log_attr('title', title)

    def do_send_group(self):
        group = self.args.do_send_group
        m = CommitMachine(self.args)
        m.set_start('make_cover')
        m.run(group)

    @staticmethod
    def do_log_update():
        Commit.update_log()

    def do_clone(self):
        no_content = self.args.no_content
        key = self.args.do_clone
        commit = Commit.find_key(key)
        if not commit:
            print(_('commit.no_continue'))
            exit(1)

        machine = CommitMachine(self.args)
        machine.set_start('clone')
        machine.commit = commit
        machine.run((key, no_content))

    def do_log_delete(self):
        key = self.args.do_log_delete
        Commit.delete(key)


def parse_args():
    parser = argparse.ArgumentParser(prog='autopatch.py')

    sub_parser = parser.add_subparsers(description=_('args.usage'))
    commit_parser = sub_parser.add_parser('commit', help=_('args.commit'))

    commit_parser.set_defaults(action=('commit', PatchOps.dispatch))
    commit_parser.add_argument('-p', '--prepare', help=_('args.prepare'),
                               action='store_true', dest='do_prepare',
                               required=False)
    commit_parser.add_argument('-c', '--continue', help=_('args.continue'),
                               action='store_true', dest='do_continue',
                               required=False)
    commit_parser.add_argument('-n', '--new', help=_('args.new'),
                               dest='do_new_version', metavar='key',
                               required=False)
    commit_parser.add_argument('-r', '--restore', help=_('args.restore'),
                               dest='do_restore', metavar='key',
                               required=False)
    commit_parser.add_argument('--clone', help=_('args.clone'),
                               dest='do_clone', metavar='key',
                               required=False)
    commit_parser.add_argument('--no-content', help=_('args.no-content'),
                               dest='no_content', action='store_true',
                               required=False)
    commit_parser.add_argument('--group', help=_('args.group'),
                               dest='group', metavar='group',
                               required=False)
    commit_parser.add_argument('--send-group', help=_('args.send-group'),
                               dest='do_send_group', metavar='group',
                               required=False)

    init_parser = sub_parser.add_parser('init', help=_('args.init'))
    init_parser.set_defaults(action=('init', None))

    log_parser = sub_parser.add_parser('log', help=_('args.log'))
    log_parser.set_defaults(action=('log', PatchOps.dispatch))
    log_parser.add_argument('-g', '--group', help=_('args.log.group'),
                            dest='do_log_group', metavar='group',
                            required=False)
    log_parser.add_argument('-c', '--clear', help=_('args.clear'),
                            action='store_true',
                            dest='do_log_clear', required=False)
    log_parser.add_argument('-d', '--delete', help=_('args.delete'),
                            dest='do_log_delete', required=False,
                            metavar='key')
    log_parser.add_argument('-s', '--status', help=_('args.status'),
                            dest='do_change_status', required=False,
                            metavar='status')
    log_parser.add_argument('-k', '--key', help=_('args.key'),
                            dest='key', required=False,
                            metavar='key')
    log_parser.add_argument('-u', '--update', help=_('args.update'),
                            dest='do_log_update', required=False,
                            action='store_true', )
    log_parser.add_argument('-t', '--title', help=_('args.title'),
                            dest='do_change_title', required=False,
                            metavar='title')

    parsed_args = parser.parse_args()
    if not parsed_args.__dict__:
        parser.print_help()
        exit(0)

    return parsed_args


init_user()
args = parse_args()

init_workspace()
init_git()
init_commit()

(action, func) = args.action
func and func(args, action)
