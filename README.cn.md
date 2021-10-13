# autopatch

一个基于python3的Linux内核补丁提交工具。

## 安装

下载本工具，并将其解压到目录/xxx/，并创建个软连接以方便使用，比如：
```shell
ln -s /xxx/autopatch.py ~/.local/bin/autopatch
```
然后，就可以运行命令autopatch了（前提是~/.local/bin/在你的PATH环境变量中，如果不在的话也可以创建软连接到/usr/bin/目录）

该工具存在一些依赖项需要安装，首先是pythondialog库：
```shell
python3 -m pip install pythondialog --user
```

对于ubuntu/debian用户，运行以下命令:
```shell
sudo apt install dialog, git, git-email
```

对于centos用户，执行以下命令：
```shell
sudo yum install dialog, git, git-email
```

## 补丁制作和提交

使用`autopatch -h`可以看到使用说明，首次使用会提示选择语言：
```shell
autopatch -h
usage: autopatch.py [-h] {commit,send,init,log} ...

optional arguments:
  -h, --help            show this help message and exit

subcommands:
  各个参数的使用方法

  {commit,send,init,log}
    commit              提交补丁
    send                进行补丁的发送
    init                初始化当前目录为工作空间
    log                 查看记录
```

### 内核准备

克隆一份开源社区上的最新代码，作为开发者最好使用next分支：
```shell
git clone https://kernel.source.codeaurora.cn/pub/scm/linux/kernel/git/next/linux-next.git
```

下载好后，需要配置git仓库的用户名和邮箱，以用于后续的补丁提交，在内核根目录中执行以下命令：
```
git config user.name "San Zhang"
git config user.email "sample@xx.com"
```

除此之外，还需要配置SMTP服务器用于邮件的发送（即用来发送补丁的邮箱），这里以GMail为例，其配置命令为：
```shell
git config sendemail.smtpServer smtp.gmail.com
git config sendemail.smtpServerPort 587
git config sendemail.smtpUser your.email@gmail.com
git config sendemail.smtpPass <your password>
git config sendemail.smtpEncryption tls
```
**注意**：请确保所使用的的邮箱开启了SMTP服务。

### 工作空间

在进行补丁提交之前，需要创建个目录作为补丁提交的“工作空间”，该“工作空间”用于存储补丁信息以及一系列的元数据信息。
请不要在内核目录中创建“工作空间”。“工作空间”创建后，其在该目录中执行`autopatch init`命令进行工作空间的初始化。

### 补丁提交

前面的准备工作完成后，就可以进行补丁的提交了。首先，像平时一样在内核目录中进行代码的编辑。内核修改完成后，在工作目录中运行`autopatch commit`进行补丁的创建和发送。 使用`autopatch commit -h`可以看到更多的使用说明。

### 补丁继续

如果补丁提交过程被打断（比如checkpatch补丁格式检查没通过），那么可以在当前的基础上对内核代码进行修改来完善，完成后使用命令`autopatch commit -c`或者`checkpatch commit --continue`来继续提交流程。

这个命令会根据当前git仓库中的提一条提交日志的标题来从工作空间中找到一个匹配的提交记录，并继续该提交的进行。

### 系列补丁

如果一个功能需要被拆分成多个补丁来发送，那么这几个补丁就组成了一个系列补丁。系列补丁中的每个补丁，在首次提交的时候（即创建的时候）需要指定`-g <group>`参数用于指定该补丁所属于的系列，其中`group`可以通过具体的功能来自己定义，例如：`autopatch commit -g series_test`。

每个补丁在系列补丁中的顺序是根据其创建的顺序来决定的，该顺序目前不可修改。系列补丁与普通补丁不同，普通补丁的提交流程最后会进行补丁的发送，而系列补丁不会。系列不会需要在所有的补丁都完成后，使用命令`autopatch send -g <group`来进行发送。补丁发送的时候，需要编辑系列补丁的“封面”，即描述整个系列补丁的功能以及每个补丁的大致情况。这个封面不会进入提交日志，因此可以写的比较随意。

## 提交管理

`autopatch log`是用来对提交记录进行管理的命令，直接输入该命令会列出当前工作空间中的所有提交记录，如下所示：
```
$ autopatch log
key          create date          update date          version  group    order  status     title               
c5f1da773960 2021-01-07 18:00:28  2021-01-07 18:51:22  v1       0        0      applied    net/bridge: fix misspellings using codespell tool
6b13ab3e3b72 2021-01-11 02:34:29  2021-01-11 02:41:26  v1       0        0      applied    net: core: use eth_type_vlan in __netif_receive_skb
```

### 提交恢复

使用命令`autopatch log -r <key>`命令可以将该补丁恢复至git仓库，包括补丁提交日志。如果只是想把提交记录恢复至git仓库，而不应用具体补丁的修改内容，那么可以通过添加`--no-content`实现，即`autopatch log -r <key> --no-content`。

如果要恢复的补丁是个系列补丁，那么该操作会将依赖的补丁（当前补丁之前的补丁）也一并恢复到git仓库。

### 新版本制作

补丁在新创建的时候，版本为V1。如果社区维护者对提交的补丁提出了修改意见，那么需要在现有的基础上做V2、V3版本。如果当前git仓库的最新提交不是我们要操作的记录，那么需要先使用上面的命令对提交进行恢复，然后使用命令`autopatch log -n <key>`来对提交进行升级。

完成代码修改后，使用`autopatch commit -c`继续补丁的提交。

### 导入导出

使用命令`autopatch log -o`可以进行当前工作空间提交记录的导出，通过指定参数`-k <key>`可导出指定记录；指定参数`-g <group>`可导出指定分组（系列补丁）。如果未指定参数的话，那么会导出当前工作空间内的所有补丁。补丁会被导出到当前工作空间中的`autopatch-export.json`中。

将`autopatch-export.json`文件拷贝到新的工作空间，并执行命令`autopatch log -i`即可完成提交的导入。如果当前工作空间存在系统的提交，那么会保留更新的那一个。
