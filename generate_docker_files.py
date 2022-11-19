import argparse
import sys
import yaml


def open_file(app_name):
    with open("voseq_apps.yml", "r") as handle:
        data = yaml.load(handle.read(), Loader=yaml.FullLoader)

    if app_name not in data:
        sys.exit(f'{app_name} not found in available apps {list(data.keys())}')

    app_data = data[app_name]
    print(app_data)

    files_and_data = [
        # file, data to replace, data to replace with
        ('config.json', 'voseq', app_name),
        ('voseq/settings/base.py', 'APP_NAME = "voseq"', f'APP_NAME = "{app_name}"'),
        ('run/docker/.env', 'voseq', app_name),
        ('run/docker/postgres/init-user-db.sh', 'voseq', app_name),
        ('run/scripts/get_project_vars', 'voseq', app_name),
        ('run/docker/docker-compose.yml', 'image: voseq', f'image: {app_name}'),
        ('run/docker/docker-compose.yml', '8081', app_data['http_port']),
        ('run/docker/docker-compose.yml', '4431', app_data['https_port']),
        ('run/docker/docker-compose.yml', 'voseq_db', f'{app_name}_db'),
        ('run/docker/docker-compose.yml', 'voseq_app', f'{app_name}_app'),
        ('run/docker/docker-compose.yml', 'voseq_nginx', f'{app_name}_nginx'),
    ]
    for item in files_and_data:
        with open(item[0], 'r') as handle:
            data = handle.read()

        data = data.replace(item[1], str(item[2]))
        with open(item[0], 'w') as handle:
            handle.write(data)


def main():
    parser = argparse.ArgumentParser(description="Generate docker files")
    parser.add_argument(
        '-a',
        '--app_name',
        dest="app_name",
        action="store",
        required=True,
    )
    args = parser.parse_args()
    print(f'Will generate docker files for app "{args.app_name}"')
    open_file(args.app_name)


if __name__ == "__main__":
    main()
