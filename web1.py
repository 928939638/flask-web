from flask import Flask,render_template,request,session,redirect,url_for,g
import config
from exts import db
from models import User,Question,Answer
from sqlalchemy import or_
from login_required import login_required


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
def index():
    context = {
        'questions':Question.query.order_by('-create_time').all()
    }
    return render_template('index.html',**context)

@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return '改手机号码已经被注册了'
        else:
            if password1 != password2:
                return '两次密码不相同，请重新输入。'
            else:
                user = User(telephone=telephone,username=username,password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone,User.password == password).first()
        if user:
            #如果user存在于数据库中，就把该uer存到session中
            session['user_id'] = user.id
            #如果想在31内保持登录
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return '手机号码或者密码错误，请重试！'

@app.route('/logout/')
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))

@app.route('/question/',methods=['GET','POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question_model = Question(title=title,content=content)
        #重要：添加question_model.author
        question_model.author = g.user
        db.session.add(question_model)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/detail/<id>')
def detail(id):
    question_model = Question.query.get(id)
    return render_template('detail.html',question=question_model)

@app.route('/comment/',methods=['POST'])
@login_required
def comment():
    question_id = request.form.get('question_id')
    content = request.form.get('content')
    answer_model = Answer(content=content)
    answer_model.author = g.user
    answer_model.question = Question.query.get(question_id)
    db.session.add(answer_model)
    db.session.commit()
    return redirect(url_for('detail',id=question_id))

@app.route('/search/')
def search():
    q = request.args.get('q')
    questions = Question.query.filter(or_(Question.title.contains(q),Question.content.contains(q)))
    context = {
        'questions':questions
    }
    return render_template('index.html',**context)

@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user = user

@app.context_processor
def context_process():
    if hasattr(g,'user'):
            return {'user':g.user}
    return {}

#before_request > 视图函数 > context_process

if __name__ == '__main__':
    app.run()
