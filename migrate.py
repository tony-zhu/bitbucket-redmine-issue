import getopt
import os
from rauth import OAuth1Service
import requests
from configman import Namespace, ConfigurationManager


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
        short_form='r'
    )
    return definition


def load_issues_by_api(consumer_key, consumer_secret, bb_user, bb_repo):

    if bb_user is None or bb_repo is None:
        print("Bitbucket not set up!")


    bitbucket = OAuth1Service(
        name='bitbucket',
        consumer_key=bb_consumer_key,
        consumer_secret=bb_consumer_secret,
        request_token_url='https://bitbucket.org/api/1.0/oauth/request_token',
        access_token_url='https://bitbucket.org/api/1.0/oauth/access_token',
        authorize_url='https://bitbucket.org/api/1.0/oauth/authenticate',
        base_url='https://bitbucket.org/api/1.0/')

    CALL_BACK = 'http://localhost?dump'

    # Make the request for a token, include the callback URL.
    request_token, request_token_secret = bitbucket.get_request_token(params={'oauth_callback': CALL_BACK})
    authorize_url = bitbucket.get_authorize_url(request_token)

    print 'Visit this URL in your browser:\n' + authorize_url
    pin = raw_input('Enter PIN from browser: ')

    session = bitbucket.get_auth_session(request_token,
                                         request_token_secret,
                                         method='POST',
                                         data={'oauth_verifier': pin})

    url = "https://bitbucket.org/api/1.0/repositories/%s/%s/issues/" % (bb_user, bb_repo)
    resp = session.get(url)
    return resp.json()

if __name__ == '__main__':
    definition = define_config()
    value_sources = ('./migrate.ini', os.environ, getopt)
    config_manager = ConfigurationManager(definition, values_source_list=value_sources)
    config = config_manager.get_config()

    bb_consumer_key = config['bitbucket-consumer-key']
    bb_consumer_secret = config['bitbucket-consumer-secret']
    bb_user = config['bitbucket-user']
    bb_repo = config['bitbucket-repo']

    if bb_consumer_key and bb_consumer_secret and bb_user and bb_repo:
        issue_dict = load_issues_by_api(bb_consumer_key, bb_consumer_secret, bb_user, bb_repo)
        print issue_dict
