# Pocket-Chat
:rocket: 最近使用python自研了一个便利性极佳的随身聊天应用`Pocket Chat`，可以使用快捷键在任意位置拾取光标选取的内容与AI交互，适合于简单的Chat任务，比如单词翻译、名词查询等。目前仅对linux系统下的应用做了开发，其他系统也可以使用，但会少些许功能。

<img src='./pocket_chat.gif'>


注意，这里使用的大模型API来自于：[DeepSeek官网](https://platform.deepseek.com)。因此也使用该API的规则(对标openai)进行模型嵌入。如果使用其他模型，则需要对源码中`ChatAPI`类进行修改。

本文以linux为例，讲解下`Pocket Chat`的部署过程。


## :one: 准备工作

配置环境如下：
```bash
sudo apt-get install xclip
pip install openai pynput PySide6
```

## :two: 应用部署

${\color{#E16B8C}{①}}$将源码(见**chat.py**)中的`#TODO`注释部分按照自己的情况进行修改，将源码命名并放在合适的路径比如： `/home/username/chat.py`。将以下图片(也可以自己找一个)保存为：`/home/username/Pictures/chatrbt.png`。

<img src='https://i-blog.csdnimg.cn/direct/45ddfcfbc07647ea87d5f5444f063ae2.png' width='300'>

${\color{#E16B8C}{②}}$创建桌面快捷方式：
```bash
sudo touch ~/.local/share/applications/chat.desktop
sudo gedit chat.desktop
```
在`chat.desktop`内填入以下内容：
```bash
[Desktop Entry]
Type=Application
Exec=gnome-terminal -- bash -c "python3 /home/username/chat.py; exec bash"
Name=Chat
Terminal=true
Icon=/home/username/Pictures/chatrbt.png
```
${\color{#E16B8C}{③}}$此时你可以Win+A搜索Chat，找到应用并打开，效果如下图所示：

<img src='https://i-blog.csdnimg.cn/direct/4b11f026486942c38e8d4402bc830b47.png'>

接下来，保持这个终端不关闭，并按照以下说明进行使用：
>1.运行脚本 python3 chat.py 这是先决条件（可以根据操作系统创建桌面图标来运行，已运行）<br>
>2.按快捷键 `<ctrl>+<f1>` 即可在光标处弹出对话框 (源码可以更改设置) <br>
>3.输入问题按Enter发送，按Esc退出 <br>
>4.按Esc退出后，再次按快捷键 `<ctrl>+<f1>` 即可在光标处弹出对话框 <br>
>5.另外Linux支持打开窗口时，将选中的文本自动填充到输入框

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/19f3318bb2924b5b8a1d91574f263107.png)
