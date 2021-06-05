from tempfile import NamedTemporaryFile, TemporaryDirectory
import json
import os
import re
import uuid
from shutil import copyfile
from config import *
from datetime import datetime, timedelta
from git import git
from langs import _


class Commit:

    @staticmethod
    def get_commits():
        return wconfig.setdefault('commits', [])

    @staticmethod
    def log_export(patches):
        for p in patches:
            if not p:
                continue
            patch = patch_path(p['patch'])
            if not os.path.exists(patch):
                continue
            with open(patch, 'r') as f:
                p['patch_data'] = f.read()
            print('export commit:%s' % p['title'])
        with open('autopatch-export.json', 'w+') as f:
            f.write(json.dumps(patches, cls=ComplexEncoder))

    @staticmethod
    def format_commit(commit):
        commit['create'] = datetime.strptime(
            commit['create'], '%Y-%m-%d %H:%M:%S')
        commit['update'] = datetime.strptime(
            commit['update'], '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def log_import(path):
        with open(path, 'r') as f:
            patches = json.loads(f.read())
        for p in patches:
            Commit.format_commit(p)
            exist_p = Commit.find_key(p['key'])
            if exist_p and exist_p['update'] > p['update']:
                print('newer commit found:%s' % p['title'])
                continue
            patch = patch_path(p['patch'])
            exist_p and Commit.delete(p['key'])
            with open(patch, 'w+') as f:
                f.write(p.pop('patch_data'))

            Commit.get_commits().append(p)
            print('import commit:%s' % p['title'])
        Commit.store_commit()

    @staticmethod
    def init_commits():
        commits = Commit.get_commits()
        [Commit.format_commit(c) for c in commits]

    @staticmethod
    def last_commit():
        commits = Commit.get_commits()
        if commits:
            return commits[-1]
        return None

    @staticmethod
    def add_commit(title, key, group=0, order=0):
        commits = Commit.get_commits()
        commit = {
            "title": title,
            "key": key,
            "create": datetime.now(),
            "update": datetime.now(),
            "patch": '',
            "version": 1,
            "parent": '',
            "group": group,
            "order": order
        }
        commits.append(commit)
        return commit

    @staticmethod
    def update_commit(commit, status=None):
        if status:
            commit['status'] = status
        update_wconfig()

    @staticmethod
    def store_commit():
        update_wconfig()

    @staticmethod
    def find_key(key):
        commits = Commit.get_commits()
        for i in commits:
            if i['key'] == key:
                return i
        return None

    @staticmethod
    def find_continue(title):
        commits = Commit.get_commits()
        return [i for i in commits if i['title'] == title and i['status'] not in ['finish', 'applied']]

    @staticmethod
    def find_group(group):
        data = [i for i in Commit.get_commits() if i['group'] == group]
        data.sort(key=lambda x: x['order'])
        return data

    @staticmethod
    def find_patch(patch):
        for i in Commit.get_commits():
            if i['patch'] == patch:
                return i
        return None

    @staticmethod
    def max_order(group):
        groups = Commit.find_group(group)
        if not groups:
            return 0
        return groups[-1]['order']

    @staticmethod
    def delete(key):
        commit = Commit.find_key(key)
        if not commit:
            return
        Commit.get_commits().remove(commit)
        patch = patch_path(commit['patch'])
        if os.path.exists(patch):
            os.remove(patch)
        Commit.store_commit()

    @staticmethod
    def restore(commit, no_content):
        title = git.get_last_title()

        if title == commit['title']:
            return True

        if commit['group']:
            items = [i for i in Commit.find_group(
                commit['group']) if i['order'] < commit['order']]
        else:
            items = []

        if not no_content:
            items.append(commit)

        first_order = 0
        for i in range(len(items)):
            if items[i]['title'] == title:
                first_order = i + 1
                break
        if first_order > 0:
            items = items[first_order:]
        if not items:
            return True

        for i in items:
            patch = patch_path(i['patch'])
            if not git.custom_am(patch):
                return False

        if no_content:
            patch = commit['patch']
            return git.custom_am(patch_path(patch), True)

        return True

    @staticmethod
    def format_patch(commit, group_count=1):
        patch = patch_path(commit['patch'])
        version = commit['version']
        order = commit['order']
        tag = commit['tag']
        subject = 'PATCH'

        if version != 1:
            subject += ' v' + str(version)
        if tag:
            subject += ' ' + tag
        if group_count > 1:
            subject += ' %d/%d' % (order, group_count)

        if subject == 'PATCH':
            return False
        subject = 'Subject: [%s]' % subject

        with open(patch, 'r') as f:
            data = f.read()
            data = re.sub(r'Subject: \[PATCH.*?]', subject, data)
            f.close()

        with open(patch, 'w') as f:
            f.write(data)
            f.close()

        return True

    @staticmethod
    def cover_name(patch):
        return '%s_cover.patch' % patch[:-6]

    @staticmethod
    def clone(commit: dict, key):
        new = commit.copy()
        new['key'] = key
        new['version'] = 1
        new['create'] = datetime.now()
        new['update'] = datetime.now()

        patch = new['patch']
        new_patch = '%s_%s.patch' % (patch[:-6], uuid.uuid4().hex)
        new['patch'] = new_patch
        copyfile(patch_path(patch), patch_path(new_patch))

        Commit.get_commits().append(new)
        return new

    @staticmethod
    def finish_group(group):
        groups = Commit.find_group(group)
        for g in groups:
            g['status'] = 'finish'

    @staticmethod
    def update_log():
        commits = Commit.get_commits()
        commits = [i for i in commits if i['status'] != 'applied']

        if not commits:
            return

        dialog_wait()
        git.git_dist_clean()

        since = (datetime.now() + timedelta(days=-120)).strftime('%Y-%m-%d')
        logs = git.git_cmd_str(
            'git log --format=%%s --author="%s" --since="%s"' % (git.get_email(), since))
        logs = logs.splitlines()

        updated = [c for c in commits if c['title'] in logs]
        for c in updated:
            c['status'] = 'applied'
        updated = [c['title'] for c in updated]

        Commit.store_commit()
        clear_screen()
        print('update finished, following commits updated:')
        print('\n'.join(updated)) if updated else print('None')


def init_commit():
    Commit.init_commits()


class CommitMachine:
    def __init__(self, args):
        self.group = None
        self.commit = None
        self.args = args
        self.start_state = None

    def set_start(self, start):
        self.start_state = start

    def run(self, state_args=None):
        handler = getattr(self, self.start_state or 'start')
        while handler:
            if state_args:
                next_state, state_args = handler(state_args)
            else:
                next_state, state_args = handler()

            if not next_state:
                update_wconfig()
                break
            handler = getattr(self, next_state)

    def pause(self, next_status=None):
        if self.commit and next_status:
            self.commit['status'] = next_status
        Commit.store_commit()
        return None, next_status

    @staticmethod
    def next(status=None, args=None):
        return status, args

    def finish(self):
        if self.group:
            Commit.finish_group(self.group)
        return self.pause('finish')

    def send_test(self, patches):
        if 'test_email' not in wconfig:
            code, msg = d.inputbox(_('commit.test_email'), title=_(
                'commit.test_email_info'), init='')
            clear_screen()
            if code != d.OK:
                return self.pause('re_commit')
            wconfig['test_email'] = msg
            update_wconfig()

        test_email = wconfig['test_email']
        return n('send_email', (patches, test_email, test_email))

    def send_email(self, info):
        """
        send email to kernel or test
        :param info:
        :return:
        """

        patches, to, cc = info
        cmd = 'git send-email --from %s --to %s --cc %s %s' % (
            git.get_from(), to, cc, ' '.join(patches))
        p = git.popen(cmd)
        p.communicate()

        if p.returncode != 0:
            return self.pause('re_commit')
        return n('finish')

    def clone(self):
        self.commit = Commit.clone(self.commit, uuid.uuid4().hex[:12])
        return n('restore')

    def select_mt(self, patches):
        """
        select maintainer the patch send to
        :param patches: patches to be send
        :return:
        """

        commit = self.commit
        cc_bk = commit.get('cc') or []
        to_bk = commit.get('to') or []

        # get maintainer from patches
        dialog_wait()
        patch_str = ' '.join(patches[1:]) if len(patches) > 1 else patches[0]
        mt_str = git.git_cmd_str('./scripts/get_maintainer.pl %s' % patch_str)
        mts = git.mt_parse(mt_str)
        clear_screen()
        if not mts:
            print(_('commit.no_mt'))
            return self.pause('re_commit')

        mts_email = [i['email'] for i in mts]
        mts.extend([{'email': i, 'name': i}
                   for i in cc_bk + to_bk if i not in mts_email])

        # select recipients, default none
        print(_('commit.select_mt'))
        while True:
            choices = [(mt['email'], mt['name'], mt['email'] in to_bk)
                       for mt in mts]
            code, recipients = d.checklist(_('commit.select_to'),
                                           extra_button=True,
                                           choices=choices,
                                           extra_label=_('dialog.button_new'))
            clear_screen()

            if code == d.CANCEL:
                print(_('commit.no_to'))
                return self.pause('re_commit')

            # new recipients should be added
            if code == d.EXTRA:
                code, msg = d.editbox_str('', title=_('commit.new_mt'))
                if code != d.OK:
                    continue
                mts += [{'email': i, 'name': i} for i in msg.splitlines() if i]
                continue

            to = ','.join(recipients)
            break

        # select Cc, default the rest
        choices = [(mt['email'], mt['name'], True)
                   for mt in mts
                   if mt['email'] not in recipients]
        code, ccs = d.checklist(_('commit.select_cc'), choices=choices)
        clear_screen()
        if code != d.OK:
            print(_('commit.no_cc'))
            return self.pause('re_commit')
        cc = ','.join(ccs)

        commit['cc'] = ccs
        commit['to'] = recipients
        Commit.store_commit()

        return n('send_email', (patches, to, cc))

    def select_send(self, patches):
        code, msg = d.menu(_('commit.send_target'),
                           choices=[('kernel', _('commit.to_kernel')), ('test', _('commit.to_test'))])
        clear_screen()
        if code != d.OK:
            return self.pause('re_commit')

        return n('select_mt', patches) if msg == 'kernel' else n('send_test', patches)

    def re_commit(self):
        if not self.args.no_add:
            cmd = 'git add ./ && git commit --amend'
        else:
            cmd = 'git commit --amend'
        commit = self.commit
        new_version = commit['version'] != 1
        tmp = NamedTemporaryFile('w+t') if new_version else None

        if new_version:
            msg = git.get_last_msg()
            msg = '%s\n%s' % (_('commit.version').format(
                version=self.commit['version']), msg)
            tmp.write(msg)
            tmp.flush()
            cmd = "%s --edit -F %s" % (cmd, tmp.name)
            if not git.current_signed():
                cmd += ' -s'

        p = git.popen(cmd)
        p.communicate()
        tmp and tmp.close()

        if p.returncode != 0:
            return n()

        commit['title'] = git.get_last_title()
        commit['update'] = datetime.now()

        return n('store')

    def check_patch(self, patches):
        err = False
        for p in patches:
            dialog_wait()
            code, msg = git.git_cmd('./scripts/checkpatch.pl %s' % p)
            if code == 0:
                continue
            code = d.scrollbox('%s\n%s' % (_('commit.checkpatch_err'), msg),
                               extra_button=True, extra_label=_('dialog.button_ignore'))
            clear_screen()
            err = True
            if code == d.OK:
                return self.pause('re_commit')

        if not err:
            d.msgbox(_('commit.checkpatch_ok'))
            clear_screen()

        if self.commit and self.commit['group'] and not self.group:
            return self.pause('re_commit')

        return n('select_send', patches)

    def restore(self):
        commit = self.commit

        if not Commit.restore(commit, self.args.no_content):
            print(_('commit.restore_err'))
            return n()

        return self.pause('re_commit')

    def new_version(self, key):
        commit = Commit.find_key(key)
        if not commit:
            print(_('commit.not_found'))
            return n()

        new_version = commit['version'] + 1
        if commit['group']:
            groups = Commit.find_group(commit['group'])
            for c in groups:
                c['version'] = new_version
        else:
            commit['version'] = new_version
        self.commit = commit

        return n('restore')

    @staticmethod
    def review_patch(patches):
        if d.yesno(_('commit.review')) == d.OK:
            for p in patches:
                p = git.popen('vim %s' % p)
                p.communicate()
        clear_screen()
        return n('check_patch', patches)

    def set_tag(self):
        commit = self.commit
        patch = patch_path(commit['patch'])
        tag = commit.get('tag') or ''
        group = commit['group']
        group_count = 1

        if group:
            group_count = len(Commit.find_group(group))

        code, tag = d.inputbox('tag, such as net-next, bpf-next', init=tag)
        clear_screen()
        if code != d.OK:
            return self.pause('set_tag')

        commit['tag'] = tag
        Commit.format_patch(commit, group_count)

        return n('review_patch', [patch])

    def store(self):
        if not os.path.exists(patch_path()):
            os.mkdir(patch_path())

        commit = self.commit
        if commit['patch'] and os.path.exists(patch_path(commit['patch'])):
            os.remove(patch_path(commit['patch']))

        patch = git.git_cmd_str('git format-patch -1 -o %s' % patch_path())
        patch = os.path.basename(patch)

        commit['patch'] = patch
        commit['title'] = git.get_last_title()

        return n('set_tag')

    def make_cover(self, group):
        groups = Commit.find_group(group)
        first = groups[0]
        count = len(groups)
        self.group = group
        self.commit = first

        cover = first.get('cover')
        tmp_file = NamedTemporaryFile('w+')
        if cover:
            tmp_file.write(cover)
            tmp_file.flush()
            tmp_file.seek(0)
        p = git.popen('vim %s' % tmp_file.name)
        p.communicate()

        cover = tmp_file.read()
        tmp_file.close()
        if not cover:
            return n()

        first['cover'] = cover
        tmp = TemporaryDirectory()
        git.git_cmd_str(
            'git format-patch --cover-letter -s -%d -o %s' % (count, tmp.name))
        tmp_cover_file = os.path.join(tmp.name, '0000-cover-letter.patch')

        f = open(tmp_cover_file, 'r')
        data = f.read()
        f.close()
        data = re.sub(r'\*\*\*[\s\S]*\*\*\*', cover, data)
        f = open(tmp_cover_file, 'w+')
        f.write(data)
        f.close()

        cover_file = Commit.cover_name(first['patch'])
        git.git_cmd('mv "%s" "%s"' % (tmp_cover_file, patch_path(cover_file)))
        tmp.cleanup()

        cover_cmt = first.copy()
        cover_cmt['patch'] = cover_file
        cover_cmt['order'] = 0

        groups.insert(0, cover_cmt)

        for g in groups:
            Commit.format_patch(g, count)

        return n('review_patch', [patch_path(g['patch']) for g in groups])

    @staticmethod
    def send_group(group):
        groups = Commit.find_group(group)
        if not groups or len(groups) < 2:
            print('invalid group')
            return n()

        return n('make_cover', group)

    @staticmethod
    def select_template():
        dialog_wait()
        templates = get_templates()
        if not templates:
            return n()
        choices = [i for i in templates.items()]
        choices.sort(key=lambda x: x[0])
        code, msg = d.menu(_('commit.select_template'), choices=choices)
        if code != d.OK:
            return n()

        template = get_template(msg)
        return n('do_commit', template)

    def do_commit(self, template):
        group = self.args.group or 0
        order = 0
        if group:
            order = Commit.max_order(group)
            if not order:
                if d.yesno(_('commit.new_group')) != d.OK:
                    return n()
            order += 1

        if not self.args.no_add:
            git.git_cmd_str('git add ./')
        p = git.popen('git commit -t %s' % template)
        p.communicate()

        if p.returncode != 0:
            print(_('commit.no_commit'))
            git.git_cmd_str('git reset HEAD')
            return n()

        git.git_cmd_str('git commit -s --amend --no-edit')
        self.commit = Commit.add_commit(
            git.get_last_title(), git.get_last_sid(), group, order)

        return n('store')

    def confirm_commit(self):
        if self.args.no_add:
            return n('select_template')

        dialog_wait()
        changes = git.git_cmd_str('git status --short')

        msg = '%s\n%s' % (_('commit.commit'), changes)
        code = d.scrollbox(msg,
                           extra_button=True, extra_label=_('dialog.button_cancel'))
        clear_screen()
        if code != d.OK:
            return n()

        return n('select_template')

    @staticmethod
    def start():
        return n('confirm_commit')


n = CommitMachine.next
