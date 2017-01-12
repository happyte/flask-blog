# 基于flask的博客系统搭建
- 1.部署在阿里云的链接为:http://123.57.132.125, 欢迎大家使用,目前360和ie浏览器不兼容。
- 2.部署在heroku网站的链接为:https://hlin2017.herokuapp.com
- 3.下载代码到本地，先建立一个virtualenv坏境，我用的是pycharm软件，直接可以建立flask坏境,如下图所示:
![image](https://github.com/happyte/flask-blog/blob/master/images/1.png)
- 4.激活virtualenv环境，`. venv/bin/activate`。安装所有requirements.txt中的模块,`pip install -r requirements.txt`。因为网络的原因可能会其中某几个会安装失败，多安装几次就好。
- 5.导入坏境变量，需要导入以下三个变量
  * export MAIL_USERNAME=<your email@example.com>(开启了smtp服务的邮箱账号，程序里默认使用163邮箱，可以修改成其它类型邮箱)
  * export MAIL_PASSWORD=<password>(不一定是你的邮箱密码，比如163邮箱开启smtp服务会让你设置一个密码，该密码即为password,qq邮箱开启smtp会提示给你一个密码)
  * export FLASK_ADMIN=<admin email>(默认是管理者邮箱，用该邮箱创建账号就是管理者)
- 6.安装数据库迁移。输入以下命令
  * `python manager.py db init` (使用init命令创建迁移仓库)
  * `python manager.py db migrate -m "initial migration"`(migrate命令用来自动创建迁移脚本)
  * `python manager.py db upgrade`(更新数据库，第一次使用该命令会新建一个数据库，可以利用pycharm右侧的Database查看该数据库)
- 7.部署程序，`python manager.py deploy`
- 8.在本地运行程序,`python manager.py runserver`打开http://127.0.0.1:5000端口查看，按Ctrl+C退出程序。

## 部署完成后的效果
![image](https://github.com/happyte/flask-blog/blob/master/images/2.png)


![image](https://github.com/happyte/flask-blog/blob/master/images/3.png)


![image](https://github.com/happyte/flask-blog/blob/master/images/4.png)


![image](https://github.com/happyte/flask-blog/blob/master/images/5.png)
