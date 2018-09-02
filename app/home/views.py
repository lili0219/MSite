#从模块的初始化文件中导入蓝图
import uuid
import datetime
import os
import json
from functools import wraps
from flask_redis import FlaskRedis
from werkzeug.security import generate_password_hash
from app.models import Tag,Movie,Preview,User,Userlog,Comment,Moviecol
from flask import render_template,request,flash,redirect,url_for,session,Response
from app import db,mainapp
from .forms import RegistForm,LoginForm,UserdetailForm,CommentForm
from . import home

rd = FlaskRedis(mainapp)

def user_login_req(f):
    """
    登录装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def change_filename(filename):
    """
    修改文件的名称
    :param filename:
    :return:
    """
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + \
        str(uuid.uuid4().hex) + fileinfo[-1]
    return filename

# 路由定义使用装饰器进行定义
@home.route('/<int:page>/')
@home.route('/')
def index(page=None):
    """
    首页电影列表
    :param page:
    :return:
    """
    tags = Tag.query.all()
    page_data = Movie.query
    #标签
    tid = request.args.get("tid",0)
    if int(tid)!=0:
        page_data = page_data.filter_by(tag_id = tid)
    #星级
    star = request.args.get("star",0)
    if int(star)!=0:
        page_data = page_data.filter_by(star=int(star))
    #时间
    time = request.args.get("time",0)
    if int(time)!=0:
        if int(time) == 1:
            page_data = page_data.order_by(
                Movie.addtime.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.addtime.asc()
            )
    #播放量
    pm = request.args.get("pm",0)
    if int(pm) !=0:
        if int(pm) == 1:
            page_data = page_data.order_by(
                Movie.playnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.playnum.asc()
            )
    # 评论量
    cm = request.args.get("cm", 0)
    if int(cm) != 0:
        if int(cm) == 1:
            page_data = page_data.order_by(
                Movie.commentnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.commentnum.asc()
            )
    if page is None:
        page = 1

    page_data = page_data.paginate(page=page,per_page=8)
    p = dict(
        tid = tid,
        star = star,
        time = time,
        pm = pm,
        cm = cm,
    )
    print("p%s"%p)
    return render_template(
        "home/index.html",
         tags=tags,
         p=p,
         page_data=page_data
    )

@home.route('/login/',methods=['GET','POST'])
def login():
    """
    登陆
    :return:
    """
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(
            username = data['name']
        ).first()
        print("user:%s"%data['pwd'])
        if user:
            if not user.check_pwd(data['pwd']):
                flash("密码错误","err")
                return redirect(url_for("home.login"))
        else:
            flash("账号不存在","err")
            return redirect(url_for("home.login"))
        session["user"] = user.username
        session["user_id"] = user.id
        userlog = Userlog(
            user_id = user.id,
            ip = request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        return redirect(url_for("home.user"))
    return render_template("home/login.html",form=form)

@home.route('/register/',methods=['GET','POST'])
def register():
    """
    会员注册
    :return:
    """
    form = RegistForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            username = data["name"],
            email = data["email"],
            phone = data["phone"],
            password   = generate_password_hash(data["pwd"]),
            uuid = uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()
        flash("注册成功","ok")
    return render_template("home/register.html",form=form)

@home.route('/logout/')
def logout():
    """
    退出登陆
    :return:
    """
    #重定向到home模块下的登陆
    session.pop("user",None)
    session.pop("user_id",None)
    return render_template(url_for("home.login"))

@home.route('/user/')
def user():
    """
    用户中心
    :return:
    """
    form = UserdetailForm()
    user = User.query.filter_by(id=int(session["user_id"])).first_or_404()
    form.face.validators = []
    if request.method == "GET":
        form.name.data = user.username
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info
    if form.validate_on_submit():
        data = form.data
        print(data)

    return render_template("home/user.html", form=form, user=user)

@home.route("/pwd/")
def pwd():
    """
    修改密码
    :return:
    """
    return render_template("home/pwd.html")

@home.route("/comments/")
def comments():
    """
    评论记录
    :return:
    """
    return render_template("home/comments.html")

@home.route("/loginlog/")
def loginlog():
    """
    登陆日志
    :return:
    """
    return render_template("home/loginlog.html")

@home.route("/moviecol/")
def moviecol():
    """
    收藏电影
    :return:
    """
    return render_template("home/moviecol.html")

@home.route("/moviecol/add/",methods=["GET"])
@user_login_req
def moviecol_add():
    """
    添加电影收藏
    :return:
    """
    uid = request.args.get("uid","")
    mid = request.args.get("mid","")
    moviecol = Moviecol.query.filter_by(
        user_id = int(uid),
        movie_id = int(mid)
    ).count()
    #已经收藏
    if moviecol == 1:
        data = dict(ok=0)
    #未收藏进行收藏
    if moviecol == 0:
        moviecol = Moviecol(
            user_id=int(uid),
            movie_id=int(mid)
        )
        db.session.add(moviecol)
        db.session.commit()
        data = dict(ok=1)
    return json.dumps(data)

@home.route("/moviecol/<int:page>/")
@user_login_req
def moviecol(page=None):
    """
    电影收藏
    :param page:
    :return:
    """
    if page is None:
        page = 1
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == session["user_id"]
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page,per_page=10)
    return render_template("home/moviecol.html",page_data=page_data)

@home.route('/animation/')
def animation():
    """
    首页轮播动画
    :return:
    """
    data = Preview.query.all()
    for v in data:
        v.id = v.id - 1
    return render_template("home/animation.html", data=data)

@home.route('/search/<int:page>/')
def search(page=None):
    """
    搜索
    :param page:
    :return:
    """
    if page is None:
        page = 1
    key = request.args.get("key","")
    movie_count = Movie.query.filter(
        Movie.title.ilike('%' + key + '%')
    ).count()
    page_data = Movie.query.filter(
        Movie.title.ilike('%' + key + '%')
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page,per_page=10)
    page_data.key = key
    return render_template("home/search.html",movie_count=movie_count,key=key,page_data=page_data)

@home.route("/play/<int:id>/<int:page>/",methods=["GET","POST"])
def play(id=None,page=None):
    """
    播放电影
    :param id:
    :param page:
    :return:
    """
    #查询出相关的标签
    movie = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id==movie.id,
        User.id == Comment.user_id
     ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page,per_page=10)
    movie.playnum = movie.playnum + 1
    form = CommentForm()
    #必须登录
    if "user" in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content = data["content"],
            movie_id = movie.id,
            user_id = session["user_id"]
        )
        db.session.add(comment)
        db.session.commit()
        movie.commentnum = movie.commentnum + 1
        db.session.add(movie)
        db.session.commit()
        flash("添加评论成功","ok")
        return redirect(url_for("home.play",id=movie.id,page=1))
    db.session.add(movie)
    db.session.commit()
    return render_template("home/play.html",movie=movie,form=form,page_data=page_data)

@home.route("/comments/<int:page>/")
@user_login_req
def comments(page=None):
    """
    个人中心评论记录
    :param page:
    :return:
    """
    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == session["user_id"]
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page,per_page=10)
    return render_template("home/comments.html",page_data=page_data)

@home.route("/video/<int:id>/<int:page>/",methods=["GET","POST"])
def video(id=None,page=None):
    """
    弹幕播放器
    :param id:
    :param page:
    :return:
    """
    movie = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    if page is None:
        page = 1

    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == movie.id,
        User.id == Comment.user_id
    ).order_by(Comment.addtime.desc()).paginate(page=page,per_page=10)
    movie.playnum = movie.playnum + 1
    form = CommentForm()
    if "user" in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content = data["content"],
            movie_id = movie.id,
            user_id=session["user_id"]
        )
        db.session.add(comment)
        db.session.commit()
        movie.commentnum = movie.commentnum + 1
        db.session.add(movie)
        db.session.commit()
        flash("添加评论成功","ok")
        return redirect(url_for("home.video",id=movie.id,page=1))
    db.session.add(movie)
    db.session.commit()
    return render_template("home/video.html",movie=movie,form=form,page_data=page_data)

@home.route("/tm/", methods=["GET", "POST"])
def tm():
    """
    弹幕消息处理
    """
    import json
    if request.method == "GET":
        # 获取弹幕消息队列
        id = request.args.get('id')
        # 存放在redis队列中的键值
        key = "movie" + str(id)
        if rd.llen(key):
            msgs = rd.lrange(key, 0, 2999)
            res = {
                "code": 1,
                "danmaku": [json.loads(v) for v in msgs]
            }
        else:
            res = {
                "code": 1,
                "danmaku": []
            }
        resp = json.dumps(res)
    if request.method == "POST":
        # 添加弹幕
        data = json.loads(request.get_data())
        msg = {
            "__v": 0,
            "author": data["author"],
            "time": data["time"],
            "text": data["text"],
            "color": data["color"],
            "type": data['type'],
            "ip": request.remote_addr,
            "_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex,
            "player": [
                data["player"]
            ]
        }
        res = {
            "code": 1,
            "data": msg
        }
        resp = json.dumps(res)
        # 将添加的弹幕推入redis的队列中
        rd.lpush("movie" + str(data["player"]), json.dumps(msg))
    return Response(resp, mimetype='application/json')
