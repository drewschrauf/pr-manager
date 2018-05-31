import json
import os
from chalice import Chalice
from github import Github

app = Chalice(app_name='pr-manager')
app.debug = True


@app.route('/', methods=['POST'])
def index():
    print(json.dumps(app.current_request.json_body))
    body = app.current_request.json_body

    g = Github(os.environ['GITHUB_TOKEN'])
    repo = g.get_repo(body['repository']['full_name'])

    action = body['action']

    if action == 'opened':
        issue = repo.get_pull(body['number']).as_issue()
        issue.add_to_labels('needs reviews')

    if action == 'submitted' or action == 'dismissed':
        pull = repo.get_pull(body['pull_request']['number'])
        approvals = 0
        rejections = 0
        for review in pull.get_reviews():
            if review.state == 'APPROVED':
                approvals += 1
            if review.state == 'CHANGES_REQUESTED':
                rejections += 1

        if approvals >= 1 and rejections == 0:
            issue = pull.as_issue()
            try:
                issue.remove_from_labels('needs reviews')
            except:
                pass
            issue.add_to_labels('mergeable')

        if rejections > 0:
            issue = pull.as_issue()
            try:
                issue.remove_from_labels('mergeable')
            except:
                pass
            issue.add_to_labels('needs reviews')


    return {'done': True}
