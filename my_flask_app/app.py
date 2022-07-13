from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from docxtpl import DocxTemplate
import locale
locale.setlocale(locale.LC_ALL, "")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128), nullable=False)
    users = db.relationship('Article', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.username)######?????????????


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    sname = db.Column(db.String(20), nullable=False)
    tname = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    otdel = db.Column(db.String(30), nullable=False)
    tabnum = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    reason = db.Column(db.String(50), nullable=False)
    vid = db.Column(db.String(50), nullable=False)
    timecr = db.Column(db.Date, default=datetime.today)
    time = db.Column(db.Date, default=datetime.today)
    timend = db.Column(db.Date, default=datetime.today)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


def __repr__(self):
    return '<Article %r>' % (self.fname)

@app.route('/user')
def index():
    if 'username' in session:
        return f'Вошел как {session["username"]}'
    return 'Вы не авторизованы'


@app.route('/', methods=['POST', 'GET'])
def log():
    if request.method == "POST":
        session.pop('username', None)

        username = request.form['username']
        p_in = request.form['password']

        user = User.query.filter_by(username=username).first()  # if this returns a user, then the email already exists in database
        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            p_hash = user.password
            check = check_password_hash(p_hash, p_in)
            if check:
                session['username'] = username
                if username == "admin":
                    return redirect("/create_adm")
                else:
                    return redirect("/menu")
            else:
                return "Неверный пароль"

        else:
            return "Пользователя не существует"

    else:
        return render_template("index.html")


@app.route('/reg', methods=['POST', 'GET'])
def create_user():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()  # if this returns a user, then the email already exists in database
        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            return "Пользователь уже существует"

        passwordhash = generate_password_hash(password)

        user = User(username=username, password=passwordhash)

        try:
            db.session.add(user)
            db.session.commit()
            return redirect("/")
        except:
            return "при регистрации произошла ошибка"
    else:
        return render_template("reg.html")


@app.route('/create_adm', methods=['POST', 'GET'])
def adm():
    if request.method == "POST":
        fioname = request.form['fioname']
        admstatus = request.form['admstatus']
        session['fioname'] = fioname
        session['admstatus'] = admstatus
        return redirect("/menu")


    else:
        return render_template("create_adm.html")


@app.route('/menu')
def menu():
    if session["username"] == "admin":
        return render_template("admin.html")
    else:
        return render_template("menu.html")


@app.route('/posts/<int:id>') #вывод данных про одну анкету
def posts_det(id):
    article = Article.query.get(id)
    return render_template("posts_det.html", article=article)


@app.route('/posts/<int:id>/print')
def print(id):
    article = Article.query.get(id)
    doc = DocxTemplate("template.docx")

    dt1 = article.time
    time = dt1.strftime("%d.%B.%Y")
    dt2 = article.timend
    timend = dt2.strftime("%d.%B.%Y")
    deltatime = article.timend - article.time + timedelta(1)
    diff = deltatime.days
    context = {'status': article.status, 'diff': diff, 'admstatus': session['admstatus'], 'fioname': session['fioname'], 'otdel': article.otdel, 'fname': article.fname, 'sname': article.sname, 'tname': article.tname, 'tabnum': article.tabnum, 'phone': article.phone, 'time': time, 'timend': timend, 'reason': article.reason, 'vid': article.vid}
    doc.render(context)
    doc.save("result.docx")
    return render_template("posts_det.html", article=article)



@app.route('/posts/<int:id>/delete')
def posts_delete(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return "при удалении статьи произошла ошибка"


@app.route('/posts', methods=['POST', 'GET'])
def posts():
    if request.method == "POST":
        user = User.query.filter_by(username=session["username"]).first()
        u = user.id
        if session["username"] == "admin":
            fname = request.form['fname']
            timecr = request.form['timecr']
            if fname == "all":
                article = Article.query.order_by(Article.id.desc()).all()
            else:
                article = Article.query.filter_by(fname=fname).order_by(Article.id.desc()).all()
            if timecr:
                article = Article.query.filter_by(timecr=timecr).order_by(Article.id.desc()).all()
        else:
            article = Article.query.filter_by(user_id=u).order_by(Article.id.desc()).all()
        try:
            return render_template("posts.html", article=article)
        except:
            return "при поиске данных произошла ошибка"
    else:
        return render_template("posts.html")


@app.route('/create-article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        fname = request.form['fname']
        sname = request.form['sname']
        tname = request.form['tname']
        status = request.form['status']
        otdel = request.form['otdel']
        tabnum = request.form['tabnum']
        phone = request.form['phone']
        vid = request.form['vid']
        reason = request.form['reason']

        timebefore = request.form['time']
        time = datetime.strptime(timebefore, '%Y-%m-%d')

        timebeforend = request.form['timend']
        timend = datetime.strptime(timebeforend, '%Y-%m-%d')

        user = User.query.filter_by(username=session["username"]).first()
        u = user.id

        article = Article(fname=fname, sname=sname, tname=tname, status=status, otdel=otdel, tabnum=tabnum, phone=phone, vid=vid, reason=reason, time=time, timend=timend, user_id=u)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/menu')
        except:
            return "при добавлении данных произошла ошибка"
    else:
        return render_template("create-article.html")


@app.route('/create_adm', methods=['POST', 'GET'])
def create_admin():
    if request.method == "POST":
        fname = request.form['fname']
        sname = request.form['sname']
        tname = request.form['tname']
        status = request.form['status']
        user = User.query.filter_by(username=session["username"]).first()
        u = user.id


        article = Article(fname=fname, sname=sname, tname=tname, status=status, user_id=u)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/menu')
        except:
            return "при добавлении данных произошла ошибка"
    else:
        return render_template("create_adm.html")


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
