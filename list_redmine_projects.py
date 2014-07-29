import os
import getopt
import urlparse
import requests
from configman import Namespace, ConfigurationManager


def define_config():
    definition = Namespace()
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
    return definition

if __name__ == '__main__':

    definition = define_config()
    value_sources = ('./migrate.ini', os.environ, getopt)
    config_manager = ConfigurationManager(definition, values_source_list=value_sources)
    config = config_manager.get_config()

    rm_root = config['redmine-root']
    rm_key = config['redmine-apikey']

    project_url = urlparse.urljoin(rm_root, "projects.json")

    resp = requests.get(project_url, params={'key': rm_key})

    for p in resp.json()['projects']:
        print("%s - %s" % (p['id'], p['name']))