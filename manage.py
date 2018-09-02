from app import mainapp
from flask_script import Manager,Server
from app import db
from flask_migrate import Migrate,MigrateCommand
from app import models
manager = Manager(mainapp)
migrate = Migrate(mainapp,db)

manager.add_command("server",Server())
manager.add_command("db",MigrateCommand)

"""
需要将建立的所有的数据库模型都在dict里面声明，这样就可以在manager 的 shell 指令行来进行数据库表的创建了
python manage.py shell
db.create_all()
"""
# @manager.shell
# def make_shell_context():
#     return dict(app=app,
#                 db =db,
#                 User = models.User,
#                 Questions = Questions,
#                 Reply = Reply)

@manager.command
def createdb():
    db.create_all()
    return '创建数据库成功'

if __name__ == '__main__':
    manager.run()