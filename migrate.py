import getopt
import os
from datetime import datetime
import urlparse
import json
import requests
from rauth import OAuth1Service
from configman import Namespace, ConfigurationManager
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import signal
import sys


def define_config():
    definition = Namespace()
    definition.add_option(
        name='bitbucket-consumer-key',
        doc='BitBucket OAuth consumer key',
        short_form='k'
    )
    definition.add_option(
        name='bitbucket-consumer-secret',
        doc='BitBucket OAuth consumer secret',
        short_form='s'
    )
    definition.add_option(
        name='bitbucket-user',
        doc='BitBucket username',
        short_form='u'
    )
    definition.add_option(
        name='bitbucket-repo',
        doc='BitBucket repository',
        short_form='p'
    )

    definition.add_option(
        name='redmine-root',
        doc='Root url of redmine server',
        short_form='r'
    )
    definition.add_option(
        name='redmine-apikey',
        doc='Root url of redmine server',
        short_form='a'
    )
    definition.add_option(
        name='redmine-root',
        doc='Root url of redmine server',
        short_form='r'
    )
    definition.add_option(
        name='redmine-apikey',
        doc='Redmine API key',
        short_form='a'
    )
    definition.add_option(
        name='redmine-project-id',
        doc='Redmine project id',
        short_form='i'
    )
    return definition


def load_issues_by_api(consumer_key, consumer_secret, bb_user, bb_repo):

    class OAuthCallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            qs = {}
            path = self.path
            if '?' in path:
                path, tmp = path.split('?', 1)
                qs = urlparse.parse_qs(tmp)

            if path != '/':
                self.send_response(404)
                return

            oauth_verifier = qs['oauth_verifier'][0]

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write('Oauth verified. Go back the the app to see the results.')

            session = bitbucket.get_auth_session(request_token,
                                             request_token_secret,
                                             method='POST',
                                             data={'oauth_verifier': oauth_verifier})

            url = "https://bitbucket.org/api/1.0/repositories/%s/%s/issues/" % (bb_user, bb_repo)

            start = 0
            limit = 50
            while True:
                params = {'start': start, 'limit': limit}
                resp = session.get(url, params=params)
                json_data = resp.json()
                count = json_data['count']
                handle_issues(session, json_data['issues'])
                start += limit
                if start >= count:
                    break

            print("Finished processing.")
            signal.alarm(signal.SIGINT)

    if bb_user is None or bb_repo is None:
        print("Bitbucket not set up!")

    bitbucket = OAuth1Service(
        name='bitbucket',
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        request_token_url='https://bitbucket.org/api/1.0/oauth/request_token',
        access_token_url='https://bitbucket.org/api/1.0/oauth/access_token',
        authorize_url='https://bitbucket.org/api/1.0/oauth/authenticate',
        base_url='https://bitbucket.org/api/1.0/')

    call_back = 'http://localhost:8093?'

    # Make the request for a token, include the callback URL.
    request_token, request_token_secret = bitbucket.get_request_token(params={'oauth_callback': call_back})
    authorize_url = bitbucket.get_authorize_url(request_token)

    print('Visit this URL in your browser:\n' + authorize_url)

    try:
        server = HTTPServer(('localhost', 8093), OAuthCallbackHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()


def convert_date(in_string):
    from_format = '%Y-%m-%dT%H:%M:%S.%f'
    to_format = "%Y-%m-%d"
    t = datetime.strptime(in_string, from_format)
    return t.strftime(to_format)


def handle_issues(session, issues):
    rm_issue_url = urlparse.urljoin(rm_root, "/issues.json")
    headers = {'content-type': 'application/json'}

    status_dict = {
        'new': 1,
        'open': 2,
        'resolved': 3,
        'on hold': 2,
        'invalid': 5,
        'duplicate': 5,
        'wontfix': 6,
        'closed': 3,
    }

    for bb_issue in issues:
        #print(i)
        i_id = bb_issue['local_id']
        url = "https://bitbucket.org/api/1.0/repositories/%s/%s/issues/%s/comments" % (bb_user, bb_repo, i_id)
        resp = session.get(url)
        #print(resp.content)
        comments = resp.json()

        desp = "%s\n \nOriginally reported by %s" % (bb_issue['content'], bb_issue['reported_by']['display_name'])
        if len(comments) > 0:
            for c in comments:
                desp += "\n\n%s\nCommented by %s at %s" % (
                    c['content'], c['author_info']['display_name'], c['utc_updated_on'])

        issue = {
            'issue': {
                'project_id': rm_project,
                'status_id': status_dict[bb_issue['status']],
                'subject': bb_issue['title'],
                'description': desp,
                'start_date': convert_date(bb_issue['created_on']),
            }
        }
        json_data = json.dumps(issue)
        resp = requests.post(rm_issue_url, params={'key': rm_key}, data=json_data, headers=headers)
        print(resp.status_code)
        print(resp.content)


if __name__ == '__main__':

    definition = define_config()
    value_sources = ('./migrate.ini', os.environ, getopt)
    config_manager = ConfigurationManager(definition, values_source_list=value_sources)
    config = config_manager.get_config()

    bb_consumer_key = config['bitbucket-consumer-key']
    bb_consumer_secret = config['bitbucket-consumer-secret']
    bb_user = config['bitbucket-user']
    bb_repo = config['bitbucket-repo']


    rm_root = config['redmine-root']
    rm_key = config['redmine-apikey']
    rm_project = config['redmine-project-id']

    if bb_consumer_key and bb_consumer_secret and bb_user and bb_repo:
        load_issues_by_api(bb_consumer_key, bb_consumer_secret, bb_user, bb_repo)
        #print issue_dict
    else:
        print("Error BitBucket configure")
        exit()

