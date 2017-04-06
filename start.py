#!/Users/sbecker/envs/.default_env_3/bin/python3

import os

import click
import logbook
import yaml
_logger = logbook.Logger(__name__)


################# GENERAL FUNCS #############

def _get_env_command(dir):
    return 'cd {} && source ../.env/bin/activate'.format(dir)

def _get_pane_command(cmds):

    return '&&'.join(list(filter(None, cmds)))

def  _windows(names=[], pane_cmds=[], work_dir=None, layout='even-horizontal' ):
    w = dict()
    w['windows'] = []
    if not len(names) == len(pane_cmds):
        raise ValueError('Windows and commands are not the same length {}:{}'.format(names,pane_cmds))
    for index,name in enumerate(names):
        w['windows'].append({'window_name': name, 'layout':layout, 'panes':[_get_pane_command([_get_env_command(work_dir),pane_cmds[index]]),]})
    w['path'] = os.path.dirname(work_dir)
    w['env'] = w['path']+'.env'

    return w


################# TEMPLATES ###############
tdict = {}
tdict['infinilab'] = _windows(
    names=['shell', 'runserver', 'infinilab', 'dmns', 'db', 'terminal'],
    pane_cmds=['./manage.py shell','./manage.py runserver 5005','ssh infinilab', 'ssh infinilab-daemons','ssh infinilab-db',''],
    work_dir='/Users/sbecker/envs/infinilab/infinilab')

tdict['bro'] = _windows (
    names=['bro', 'bro-db', 'local-bro'],
    pane_cmds=['ssh bro', 'ssh bro-db', ''],
    work_dir='/Users/sbecker/envs/bro/bro'
    )

tdict['dhcpawn'] = _windows(
    names=['testserver', 'pgcli', 'terminal', 'celery worker', 'rabbitmq-server'],
    pane_cmds=['cob testserver','pgcli dhcpawn','', 'celery -A cob.celery_utils worker --loglevel=DEBUG -E -B','rabbitmq-server'],
    work_dir='/Users/sbecker/envs/dhcpawn/dhcpawn/')


tdict['p2'] = _windows(names=['term3'], pane_cmds=['ls -l'], work_dir='/Users/sbecker/envs/dhcpawn/dhcpawn/')

p3 = []

infradev = []

itzik = []

#################### END TEMPLATES ##############



@click.command()
@click.argument('tool')
def develop(tool):
    tmuxp = os.path.dirname(os.path.realpath(__file__))+'/.tmuxp'
    tmux_config_filename = os.path.abspath(tdict[tool]['path']+'/{}_tmuxconf.yml'.format(tool))
    with open(tmux_config_filename, 'w') as f:
        yaml.dump(_get_tmux_config(tool), f)
    os.chdir(tdict[tool]['path'])
    os.execve(tmuxp, [tmuxp, 'load', tmux_config_filename], {**os.environ})


def _get_tmux_config(tool):
    windows = tdict[tool]['windows']
    return {
        'session_name': tool,
        'windows': windows,
    }

if __name__=='__main__':
    develop()
