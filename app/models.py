from app import db
import datetime

class User(db.Model):
    __tablename__ = 'users'
    id       = db.Column(db.Integer,primary_key=True,autoincrement=True)
    email    = db.Column(db.String(100))
    phone    = db.Column(db.String(11))
    info     = db.Column(db.Text)
    face     = db.Column(db.String(255))
    uuid     = db.Column(db.String(255),unique=True)
    addtime  = db.Column(db.DateTime,index=True,default=datetime.datetime.now)
    username = db.Column(db.String(64))
    password = db.Column(db.String(128))

    def check_pwd(self,password):
        from werkzeug.security import check_password_hash
        print("models password:",self.password,check_password_hash(self.password,password))
        return check_password_hash(self.password,password)

class Userlog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    ip = db.Column(db.String(100))
    addtime = db.Column(db.DateTime,index=True,default=datetime.datetime.now)

    def __repr__(self):
        return '<User %r>'%self.id

class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True)
    addtime = db.Column(db.DateTime,index=True,default=datetime.datetime.now)
    movies = db.relationship("Movie",backref='tags')

    def __repr__(self):
        return "<Tag %r>"%self.name
#电影
class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    title = db.Column(db.String(255),unique=True)
    url = db.Column(db.String(255),unique=True)
    info = db.Column(db.Text)
    logo = db.Column(db.String(255),unique=True)
    star = db.Column(db.SmallInteger)#星级
    playnum = db.Column(db.BigInteger)#播放量
    commentnum = db.Column(db.BigInteger)#评论量
    tag_id = db.Column(db.Integer,db.ForeignKey('tag.id'))
    area = db.Column(db.String(255))#上映地区
    release_time = db.Column(db.Date)#上映时间
    length = db.Column(db.String(100))#播放时间
    addtime = db.Column(db.DateTime,index=True,default=datetime.datetime.now)
    comments = db.relationship("Comment",backref='movie')
    moviecols = db.relationship("Moviecol",backref='movie')

    def __repr__(self):
        return "<Movie %r>"%self.title

#上映预告
class Preview(db.Model):
    __tablename__ = "preview"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(255),unique=True)#标题
    logo = db.Column(db.String(255),unique=True)#封面
    addtime = db.Column(db.DateTime,index=True,default=datetime.datetime.now)
    def __repr__(self):
        return "<Preview %r>"%self.title

#评论
class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.Text)#评论内容
    movie_id = db.Column(db.Integer,db.ForeignKey("movies.id"))
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    addtime = db.Column(db.DateTime,index=True,default=datetime.datetime.now)

    def __repr__(self):
        return "<Comment %r>"%self.id

#电影收藏
class Moviecol(db.Model):
    __tablename__ = 'moviecol'
    id = db.Column(db.Integer,primary_key=True)
    movie_id = db.Column(db.Integer,db.ForeignKey("movies.id"))
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    addtime = db.Column(db.DateTime,index=True,default=datetime.datetime.now)

    def __repr__(self):
        return "<Moviecol %r>"%self.id

#权限
class Auth(db.Model):
    __tablename__ = "auth"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True)
    url  = db.Column(db.String(255),unique=True)
    addtime = db.Column(db.DateTime,index=True,default=datetime.datetime.now)

    def __repr__(self):
        return "<Auth %r>"%self.name

#角色
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True)
    auths = db.Column(db.String(600))
    addtime = db.Column(db.DateTime,index=True,default=datetime.datetime.now)
    admins = db.relationship("Admin",backref="role")

    def __repr__(self):
        return "<Role %r>"%self.name

#管理员
class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True)
    pwd = db.Column(db.String(100))
    is_super = db.Column(db.SmallInteger)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    addtime = db.Column(db.DateTime,index=True,default=datetime.datetime.now)
    adminlogs = db.relationship("Adminlog",backref='admin')
    oplogs = db.relationship("Oplog",backref='admin')

    def __repr__(self):
        return "<Admin %r>"%self.name

    def check_pwd(self,pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd,pwd)

#管理员登陆日志
class Adminlog(db.Model):
    __tablename__ = "adminlog"
    id = db.Column(db.Integer,primary_key=True)
    admin_id = db.Column(db.Integer,db.ForeignKey("admin.id"))
    ip = db.Column(db.String(100))
    addtime = db.Column(db.DateTime,index=True,default=datetime.datetime.now)
    def __repr__(self):
        return "<Adminlog %r>"%self.id
#操作日志
class Oplog(db.Model):
    __tablename__ = "oplog"
    id = db.Column(db.Integer,primary_key=True)
    admin_id = db.Column(db.Integer,db.ForeignKey('admin.id'))
    ip = db.Column(db.String(100))
    reason = db.Column(db.String(100))
    addtime = db.Column(db.DateTime,index=True,default=datetime.datetime.now)

    def __repr__(self):
        return "<Oplog %r>"%self.id


if __name__ == '__main__':
    db.create_all()
