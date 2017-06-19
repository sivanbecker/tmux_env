#!/usr/local/bin/python3

import os

import click
import logbook
import yaml
_logger = logbook.Logger(__name__)


################# GENERAL FUNCS #############

def _cob_dev_export():
    return 'unset __PYVENV_LAUNCHER__ && export COB_DEVELOP=1 && export COB_NO_REENTRY=1'

def _get_flask_env_command(dir):
    return 'cd {} && source ../.env/bin/activate && unset __PYVENV_LAUNCHER__ && export FLASK_DEBUG=1 && export FLASK_APP=app1.py'.format(dir)

def _get_meeseeks_env_command(dir):
    return 'cd {} && source ../.env/bin/activate && unset __PYVENV_LAUNCHER__ && export FLASK_DEBUG=1 && export FLASK_APP=meeseeks.py && export APP_SETTINGS="config.DevelopmentConfig" && export DATABASE_URL="postgresql://localhost/meeseeks"'.format(dir)

def _get_cob_env_command(dir):
    return 'cd {} && source ../.env/bin/activate && {}'.format(dir, _cob_dev_export())

def _get_infradev_env_command(dir):
    update_itzik = 'itzik update -env {}'.format(dir+'/env')
    return 'cd {} && source env/bin/activate && {}'.format(dir, update_itzik)


def _get_env_command(dir):
    if os.path.exists(os.path.realpath(os.curdir)+'/../.env'):
        return 'cd {} && source ../.env/bin/activate'.format(dir)
    elif os.path.exists(os.path.realpath(os.curdir)+'/env'):
        return 'cd {} && source env/bin/activate'.format(dir)

def _get_pane_command(cmds):

    return '&&'.join(list(filter(None, cmds)))

def  _windows(names=[], pane_cmds=[], work_dir=None, layout='even-horizontal', tool=None):
    w = dict()
    w['windows'] = []
    if not len(names) == len(pane_cmds):
        raise ValueError('Windows and commands are not the same length {}:{}'.format(names,pane_cmds))
    for index,name in enumerate(names):
        if tool:
            if tool=='dhcpawn':
                w['windows'].append({'window_name': name, 'layout':layout, 'panes':[_get_pane_command([_get_cob_env_command(work_dir),pane_cmds[index]]),]})
            elif tool=='infradev':
                w['windows'].append({'window_name': name, 'layout':layout, 'panes':[_get_pane_command([_get_infradev_env_command(work_dir),pane_cmds[index]])]})
            elif tool=='flask':
                w['windows'].append({'window_name': name, 'layout':layout, 'panes':[_get_pane_command([_get_flask_env_command(work_dir),pane_cmds[index]])]})
            elif tool=='meeseeks':
                w['windows'].append({'window_name': name, 'layout':layout, 'panes':[_get_pane_command([_get_meeseeks_env_command(work_dir),pane_cmds[index]])]})
            else:
                w['windows'].append({'window_name': name, 'layout':layout, 'panes':[_get_pane_command([_get_env_command(work_dir),pane_cmds[index]])]})

    w['path'] = os.path.dirname(work_dir)
    w['env'] = w['path']+'.env'

    return w



################# TEMPLATES ###############
tdict = {}
tdict['infinilab'] = _windows(
    names=['shell', 'runserver', 'infinilab', 'dmns', 'db', 'trm1', 'trm2', 'trm3'],
    pane_cmds=['./manage.py shell','./manage.py runserver 5005','ssh infinilab', 'ssh infinilab-daemons','ssh infinilab-db','', '', ''],
    work_dir='/Users/sbecker/envs/infinilab/infinilab',
    tool='infinilab')

tdict['bro'] = _windows (
    names=['bro', 'bro-db', 'local-bro'],
    pane_cmds=['ssh bro', 'ssh bro-db', ''],
    work_dir='/Users/sbecker/envs/bro/bro',
    tool='bro'
    )

tdict['dhcpawn'] = _windows(
    names=['testserver', 'pgcli', 'celery worker', 'rabbitmq-server', 'trm1', 'trm2', 'trm3'],
    pane_cmds=['cob testserver','pgcli dhcpawn', 'celery -A cob.celery_utils worker --loglevel=DEBUG -E -B','rabbitmq-server', '', '', ''],
    work_dir='/Users/sbecker/envs/dhcpawn/dhcpawn/',
    tool='dhcpawn')


tdict['p2'] = _windows(names=['term3'], pane_cmds=['ls -l'], work_dir='/Users/sbecker/envs/p2/p2', tool='p2')

tdict['p3'] = _windows(
    names=['trm1', 'trm2', 'trm3'],
    pane_cmds=['','',''],
    work_dir='/Users/sbecker/envs/p3/p3',
    tool='p3')


tdict['infradev'] = _windows(names=['infradev_cli_1','infradev_cli_2','trm3'],
                             pane_cmds=['cd infradev-cli/infradev_cli', 'cd infradev-cli/infradev_cli', ''],
                             work_dir='/Users/sbecker/envs/itzik/infradev/',
                             tool='infradev')

tdict['flask'] = _windows(names=['trm1','trm2','trm3'],
                          pane_cmds=['','',''],
                          work_dir='/Users/sbecker/envs/flask/app1',
                          tool='flask')

tdict['meeseeks'] = _windows(names=['trm1','trm2','trm3'],
                          pane_cmds=['','',''],
                          work_dir='/Users/sbecker/envs/flask/meeseeks/meeseeks',
                          tool='meeseeks')

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
    # import pudb;pudb.set_trace()
    os.execve(tmuxp, [tmuxp, 'load', tmux_config_filename], {**os.environ})


def _get_tmux_config(tool):
    windows = tdict[tool]['windows']
    return {
        'session_name': tool,
        'windows': windows,
    }

if __name__=='__main__':
    develop()
