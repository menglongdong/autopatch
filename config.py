import datetime
import json
import os
import subprocess
import uuid

from dialog import Dialog

from langs import _, set_lang, get_lang

config_dir = os.path.join(os.environ['HOME'], '.autopatch')
config_file = os.path.join(config_dir, 'autopatch.conf')
uconfig = {}

current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'template')

work_dir = os.getcwd()
wconfig_dir = os.path.join(work_dir, '.autopatch')
wconfig_file = os.path.join(wconfig_dir, 'default.conf')
wconfig = {}

d = Dialog(autowidgetsize=True)


def update_uconfig():
    """
    docstring
    """
    s = json.dumps(uconfig)
    with open(config_file, 'w+') as f:
        f.write(s)
        f.close()


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


def update_wconfig():
    """
    docstring
    """
    s = json.dumps(wconfig, cls=ComplexEncoder)
    with open(wconfig_file, 'w+') as f:
        f.write(s)
        f.close()


def setup_kernel():
    code, msg = d.editbox_str(wconfig.get('kernel'),
                              title=_('work.select_kernel'))
    clear_screen()

    if code != Dialog.OK:
        print('已取消！')
        exit(0)

    msg = msg.strip(' \n')
    if not os.path.exists(msg):
        print('目录不存在！')
        exit(0)

    wconfig['kernel'] = msg
    wconfig['id'] = str(uuid.uuid1())
    update_wconfig()


def init_workspace():
    if os.path.exists(wconfig_file):
        with open(wconfig_file) as f:
            wconfig.update(json.loads(f.read()))
            f.close()
            return False

    if d.yesno(_('work.init')) != Dialog.OK:
        clear_screen()
        exit(0)

    if not os.path.exists(wconfig_dir):
        os.mkdir(wconfig_dir)

    setup_kernel()
    return True


def setup_lang():
    choices = [('zh-CN', '中文'), ('en', 'English')]
    code, tags = d.menu('请选择您的语言：', choices=choices)
    clear_screen()

    if code != d.OK:
        print('未选择语言，已退出！')
        exit(0)

    uconfig['lang'] = tags
    update_uconfig()
    set_lang(tags)


def init_user():
    """
    Init config for user that first use.
    """

    if os.path.exists(config_file):
        with open(config_file) as f:
            uconfig.update(json.loads(f.read()))
            f.close()
            set_lang(uconfig['lang'])
            return False

    print(_('init.user.intro'))
    if not os.path.exists(config_dir):
        os.mkdir(config_dir)

    setup_lang()
    return True


def patch_path(patch=None):
    path = os.path.join(work_dir, 'patch')
    if patch:
        return os.path.join(path, patch)
    return path


def clear_screen():
    p = subprocess.Popen(['clear'], shell=False, stdout=None,
                         stderr=None, close_fds=True)
    p.wait()


def dialog_wait():
    d.infobox(_('commit.wait'))


def get_templates():
    templates = os.listdir(template_dir)
    data = set()
    data_dict = {}
    for i in templates:
        data.add(i.split('.')[0])
    for i in data:
        data_dict[i] = get_template_desc(i)
    return data_dict


def get_template_desc(name):
    template = get_template(name)
    if not template or not os.path.exists(template):
        return None
    with open(template) as f:
        desc = f.readline()
        f.close()
        if not desc:
            return None
        return desc.strip('# \n')


def get_template(name):
    lang = get_lang()
    template = os.path.join(template_dir, '%s.%s.txt' % (name, lang))
    if os.path.exists(template):
        return template

    template = os.path.join(template_dir, '%s.txt' % name)
    if os.path.exists(template):
        return template

    return None
