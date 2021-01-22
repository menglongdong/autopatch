# autopatch

A tool based on python3 to make submitting kernel patch easy~

## INSTALL

you can simply download the source code to /xxx/ and make a link to it, such as:
```shell
ln -s /xxx/autopatch.py ~/.local/bin/autopatch
```
Then, you can use this tool anywhere.

Before you use it, some packages are needed, you can install with these command:
```shell
python3 -m pip install pythondialog --user
```

For Ubuntu/Debian user:
```shell
sudo apt install dialog, git, git-email
```

For Centos user:
```shell
sudo yum install dialog, git, git-email
```

## Usage

You can simply use `autopatch -h` to see the usage:
```shell
autopatch -h
usage: autopatch.py [-h] {commit,init,log} ...

optional arguments:
  -h, --help         show this help message and exit

subcommands:
  How to use each parameter

  {commit,init,log}
    commit           Submit patch
    init             Initialize the current directory as a workspace
    log              View log
```

### Kernel Prepare

Simply clone the kernel source to your location. `linux-next` will be an ideal branch for developers:
```shell
git clone https://kernel.source.codeaurora.cn/pub/scm/linux/kernel/git/next/linux-next.git
```

After that, config your name and email with `git config user.name xxx` and `git config user.email xxx`.
Username and email here will be the author of patches, so make sure they are right.

Besides, you should also config your smtp server, which used to send email. If you have a gmail, do it below:
```shell
git config sendemail.smtpServer smtp.gmail.com
git config sendemail.smtpServerPort 587
git config sendemail.smtpUser your.email@gmail.com
git config sendemail.smtpPass <your password>
```

### workspace

Before starting, you should make a directory as your workspace.
Generally speaking, workspace is the place to store your data of patch submitting.
You can initialize a directory as workspace by exec `autopatch init` in it.

### Commit

After initializing workspace, you can exec `autopatch commit` to begin to submit patches to the Kernel Community.
Have fun~

With `autopatch commit -h`, you can see more usages.

