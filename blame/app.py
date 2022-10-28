import os
from flask import Flask, request, Response, render_template
from flask_recaptcha import ReCaptcha
from git import GitRepo, GitError

app = Flask(__name__, static_folder='static')

recaptcha = None
if os.getenv('RECAPTCHA_SITE_KEY', None) is not None:
    app.config['RECAPTCHA_SITE_KEY'] = os.getenv('RECAPTCHA_SITE_KEY')
    app.config['RECAPTCHA_SECRET_KEY'] = os.getenv('RECAPTCHA_SECRET_KEY')
    recaptcha = ReCaptcha(app)

TPL_INDEX = 'index.html'

@app.route('/', methods=['GET'])
def index():
    return render_template(TPL_INDEX)

@app.route('/', methods=['POST'])
def blame():
    if recaptcha is not None and not recaptcha.verify():
        return 'invalid captcha!'

    if 'repo' not in request.form:
        return render_template(TPL_INDEX, message='No repo provided')
    url = request.form.get('repo')
    if not url.startswith(('https://', 'http://')):
        return render_template(TPL_INDEX, message='Invalid repo url', repo=url)
    opts = request.form.get('opts')
    if opts is None or opts.strip() == '':
        opts = []
    else:
        opts = opts.split(' ')

    try:
        with GitRepo.from_clone(url) as repo:
            blames = list(repo.blame_all(opts=opts))
    except GitError as error:
        return render_template(TPL_INDEX, message=f'Error: {str(error)}', repo=url, opts=opts)

    blame = '\n'.join(filter(lambda x: len(x) > 0, blames))
    return render_template(TPL_INDEX, blame=blame, repo=url, opts=opts)

if __name__ == '__main__':
    app.run()
