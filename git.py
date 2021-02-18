import re
import subprocess
from tempfile import NamedTemporaryFile

from config import wconfig
from langs import _

remote_host = 'https://git.kernel.org'
remote_linux_next = remote_host + '/pub/scm/linux/kernel/git/next/linux-next.git'
remote_net_next = remote_host + '/pub/scm/linux/kernel/git/netdev/net-next.git'


class GitHelper:

    def __init__(self, path=None):
        """
        docstring
        """
        self.git_path = path

    def popen(self, cmd):
        """
        docstring
        """
        return subprocess.Popen('cd %s && %s' % (self.git_path, cmd), shell=True)

    def git_cmd(self, cmd):
        return subprocess.getstatusoutput('cd %s && %s' % (self.git_path, cmd))

    def git_cmd_str(self, cmd):
        """
        docstring
        """
        (code, res) = subprocess.getstatusoutput(
            'cd %s && %s' % (self.git_path, cmd))
        if code == 0:
            return res
        return None

    @staticmethod
    def get_patch_log(patch):
        with open(patch, 'r') as f:
            data = f.read()
            f.close()
            m = re.search(r'Subject: \[.*?] ([\s\S]*)\n---\n ', data)
            if not m:
                return None
            return m.group(1)

    def get_user(self):
        """
        docstring
        """
        return self.git_cmd_str('git config user.name')

    def get_email(self):
        """
        docstring
        """
        return self.git_cmd_str('git config user.email')

    def get_from(self):
        """
        docstring
        """
        return self.get_email()

    def custom_am(self, patch, no_content=False):

        log = git.get_patch_log(patch)
        if not log:
            return False

        tmp = NamedTemporaryFile('w+t')
        tmp.write(log)
        tmp.flush()
        cmd = 'git commit --allow-empty -F "%s"' % tmp.name
        if not no_content:
            cmd = 'git apply "%s" && git add ./ && ' % patch + cmd
        code, msg = self.git_cmd(cmd)
        tmp.close()
        if code != 0:
            return False
        return True

    def current_signed(self):
        code, msg = self.git_cmd('git log -1 | grep "Signed-off-by:"')
        return code == 0

    def find_by_title(self, title, auth=None):
        cmd = 'git log -1 --grep="%s"' % title
        if auth:
            cmd += ' --author="%s"' % auth
        return self.git_cmd_str(cmd)

    def get_sig(self):
        return '%s <%s>' % (self.git_cmd_str('git config user.name'),
                            self.git_cmd_str('git config user.email'))

    def get_last_title(self):
        """
        docstring
        """
        return self.git_cmd_str('git log --format=%s -1')

    def get_last_sid(self):
        return self.git_cmd_str('git log --format=%h -1')

    def git_clean(self):
        """
        docstring
        """
        self.git_cmd('git checkout ./ && git pull')

    def get_branch(self):
        branches = self.git_cmd_str('git branch')
        lines = branches.splitlines()
        for i in lines:
            if i.startswith('*'):
                return i.strip('* \n')
        return None

    def git_dist_clean(self):
        """
        make current branch consistent with remote
        :return: True on success, False otherwise
        """

        branch = self.get_branch()
        if not branch:
            print(_('git.invalid_branch'))
            return False
        tmp_branch = branch + '_ap_tmp'

        upstream = self.git_cmd_str(
            'git rev-parse --abbrev-ref %s@{upstream}' % branch)
        if not upstream:
            print(_('git.invalid_remote'))
            return False

        code, msg = \
            self.git_cmd('git checkout ./ && git clean -df && git checkout -b %s && '
                         'git branch -D %s && git checkout %s -b %s && '
                         'git branch -D %s && git pull' % (
                             tmp_branch, branch, upstream, branch, tmp_branch
                         ))
        if code != 0:
            print('ERROR: ' + msg)
            return False
        return True

    def get_last_msg(self):
        return self.git_cmd_str('git log --format=%B -1')

    @staticmethod
    def mt_parse(mt_str: str):
        """
        docstring
        """
        mts = mt_str.splitlines()
        mts_entry = []
        for mt in mts:
            mt = mt.strip()
            mt_entry = {}
            m = re.match(r'(.*) <(.*)> \((.*)\)', mt)
            if m:
                mt_entry['name'] = m.group(1)
                mt_entry['email'] = m.group(2)
                mt_entry['des'] = m.group(3)
            else:
                m = re.match(r'([^(]*) \((.*)\)', mt)
                if not m:
                    return None
                mt_entry['name'] = ''
                mt_entry['email'] = m.group(1)
                mt_entry['des'] = m.group(2)
            mts_entry.append(mt_entry)
        return mts_entry


git = GitHelper()


def init_git():
    if not git.git_path:
        git.git_path = wconfig['kernel']

    if not git.get_last_title():
        print(_('args.not_git'))
        exit(1)
