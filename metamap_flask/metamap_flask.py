# -*- coding: utf-8 -*
from flask import Flask, url_for, request, render_template, make_response, abort, redirect, Response
import json

app = Flask(__name__)
app.config.from_object('config')
app.config.from_pyfile('instance/config.py')
app.config.from_pyfile(app.config['APP_CONFIG_FILE'])


@app.route('/')
def index():
    return 'Index Page'


@app.route('/hello')
@app.route('/hello/<name>')
def hello(name=None):
    # return 'Hello World'
    return render_template('hello.html', name=name)


"""url里绑定变量
"""


@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username


@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id


## 后面有/和没有/是不一样的
@app.route('/projects/')
def projects():
    return 'The project page'


@app.route('/about')
def about():
    return 'The about page'


# 绑定http方法
# 取key的时候如果client端并没有提供，然后也取的时候也没放默认值，就会包错KeyError,然后前端反馈是400
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # return 'post login'
        # 对应与querystring
        return 'posr login' + request.form['user'] + ' and ' + request.form['pwd']
    else:
        # return 'get long'
        return 'get login' + request.args.get('user') + ' and ' + request.args.get('pwd', 'no passwd')


# 文件上传
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save('/var/www/uploads/uploaded_file.txt')
        # f.save('/var/www/uploads/' + secure_filename(f.filename)) 保留原文件名


# 获取cookie
@app.route('/cookie')
def cookie():
    username = request.cookies.get('username')
    # use cookies.get(key) instead of cookies[key] to not get a
    # KeyError if the cookie is missing.


# 添加cookie
@app.route('/set_cookie')
def set_cookie():
    resp = make_response(render_template(''))
    resp.set_cookie('username', 'the username')
    return resp


# 重定向
@app.route('/redirect')
def redirect():
    params = dict();
    params['user'] = 'will'
    # return redirect(url_for('login'))
    # return redirect('login?user=will')
    return redirect(url_for('projects'))


@app.route('/redirect_abort')
def redirect_abort():
    # 打印log
    app.logger.debug('A value for debugging')
    app.logger.warning('A warning occurred (%d apples)', 42)
    app.logger.error('An error occurred')
    abort(404)
    print 'this_is_never_executed()'


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404



"""
处理json
"""


# @app.route('/json', methods=['GET', 'POST'])
@app.route('/json', methods=['POST'])
def my_json():
    print request.headers
    print request.json
    rt = {'info': 'hello ' + request.json['name']}
    return Response(json.dumps(rt), mimetype='application/json')


if __name__ == '__main__':
    print('real email is %s ' % app.config['MAIL_FROM_EMAIL'])
    print('real env is %s ' % app.config['ENV'])
    app.run(host='0.0.0.0', debug=app.config['DEBUG'])
