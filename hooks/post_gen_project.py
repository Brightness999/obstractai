import os
import shutil
import stat


project_dir = os.getcwd()
deploy_dir = os.path.join(project_dir, 'deploy')
reqs_dir = os.path.join(project_dir, 'requirements')
app_dir = os.path.join(project_dir, '{{ cookiecutter.project_slug }}')

using_teams = '{{cookiecutter.use_teams}}' == 'y'
using_subscriptions = '{{cookiecutter.use_subscriptions}}' == 'y'
using_heroku = '{{ cookiecutter.deploy_platform }}' == 'heroku'
using_heroku_docker = '{{ cookiecutter.deploy_platform }}' == 'heroku_docker'
using_google_cloud_run = '{{ cookiecutter.deploy_platform }}' == 'google_cloud_run'
using_do_app_platform = '{{ cookiecutter.deploy_platform }}' == 'digital_ocean_app_platform'
using_docker = '{{ cookiecutter.use_docker }}' == 'y'
using_prod_docker = using_heroku_docker or using_google_cloud_run or using_do_app_platform

def make_executeable(filename):
    """Makes a file executable"""
    # HT: https://stackoverflow.com/a/12792002/8207
    st = os.stat(filename)
    os.chmod(filename, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


make_executeable(os.path.join(project_dir, 'manage.py'))


# see https://github.com/audreyr/cookiecutter/issues/723 for more on this approach
def remove(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)
    elif os.path.isdir(filepath):
        shutil.rmtree(filepath)

def rename_requirements(orig_prefix, final_prefix='prod'):
    os.rename(os.path.join(reqs_dir, f'{orig_prefix}-requirements.in'),
              os.path.join(reqs_dir, f'{final_prefix}-requirements.in'))
    os.rename(os.path.join(reqs_dir, f'{orig_prefix}-requirements.txt'),
              os.path.join(reqs_dir, f'{final_prefix}-requirements.txt'))


if not using_teams:
    remove(os.path.join(project_dir, 'apps', 'teams'))
    remove(os.path.join(project_dir, 'pegasus', 'apps', 'teams'))
    remove(os.path.join(project_dir, 'templates', 'teams'))
    remove(os.path.join(project_dir, 'templates', 'web', 'team_admin.html'))

if not using_subscriptions:
    remove(os.path.join(project_dir, 'assets', 'styles', 'app', 'subscriptions.sass'))
    remove(os.path.join(project_dir, 'apps', 'subscriptions'))
    remove(os.path.join(project_dir, 'templates', 'subscriptions'))
    remove(os.path.join(project_dir, 'pegasus', 'apps', 'components', 'management', 'commands', 'bootstrap_subscriptions.py'))

if not using_heroku:
    remove(os.path.join(project_dir, 'runtime.txt'))
    remove(os.path.join(project_dir, 'Procfile'))

if not using_heroku_docker:
    remove(os.path.join(project_dir, 'heroku.yml'))

if not using_do_app_platform:
    remove(os.path.join(project_dir, 'deploy'))
    remove(os.path.join(project_dir, 'requirements', 'do-requirements.in'))
    remove(os.path.join(project_dir, 'requirements', 'do-requirements.txt'))
    remove(os.path.join(app_dir, 'settings_do.py'))
else:
    rename_requirements('do')
    os.rename(os.path.join(deploy_dir, 'do', 'app-spec.yaml'),
              os.path.join(deploy_dir, 'app-spec.yaml'))


if not (using_heroku or using_heroku_docker):
    remove(os.path.join(project_dir, 'requirements', 'heroku-requirements.in'))
    remove(os.path.join(project_dir, 'requirements', 'heroku-requirements.txt'))
    remove(os.path.join(app_dir, 'settings_heroku.py'))
else:
    rename_requirements('heroku')

if not using_prod_docker:
    remove(os.path.join(project_dir, 'Dockerfile.web'))

if not using_google_cloud_run:
    remove(os.path.join(app_dir, 'settings_google.py'))
    remove(os.path.join(project_dir, '.env.production'))
    remove(os.path.join(project_dir, 'cloudmigrate.yaml'))
    remove(os.path.join(project_dir, 'scripts', 'google'))
    remove(os.path.join(reqs_dir, 'google-requirements.in'))
    remove(os.path.join(reqs_dir, 'google-requirements.txt'))
else:
    rename_requirements('google')

if not using_docker:
    remove(os.path.join(project_dir, '.env.dev'))
    remove(os.path.join(project_dir, 'Dockerfile.dev'))
    remove(os.path.join(project_dir, 'docker-compose.yml'))
    remove(os.path.join(app_dir, 'settings_docker.py'))

def migrate_renderable_templates():
    """
    For all paths in "renderable_templates", fix the file extensions and move them
    into the proper templates directory. Then clean up the folders.
    """
    renderable_template_dirs = [
        ('renderable_templates',)
    ]
    for dir_path in renderable_template_dirs:
        assert dir_path[-1] == 'renderable_templates'
        input_dir = os.path.join(project_dir, *dir_path)
        output_dir = os.path.join(project_dir, *dir_path[:-1] + ('templates', ))
        for path, subdirs, files in os.walk(input_dir):
            for filename in files:
                if filename.endswith('.renderable_html'):
                    complete_path = os.path.join(path, filename)
                    new_filename = filename.replace('.renderable_html', '.html')
                    new_path = path.replace(input_dir, output_dir)
                    new_complete_path = os.path.join(new_path, new_filename)
                    os.rename(complete_path, new_complete_path)

        # cleanup
        remove(input_dir)

def move_gitignore():
    os.rename(os.path.join(project_dir, '.gitignore.project'),
              os.path.join(project_dir, '.gitignore'))



migrate_renderable_templates()
move_gitignore()

print('New project created at: {}'.format(os.getcwd()))
