import os
import sys
import re
import click
from sqlalchemy import create_engine
from sqlalchemy import inspect
from jinja2 import Template
from pattern.text.en import singularize, pluralize
sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)


engine = create_engine(os.getenv('CELLAS_DATABASE_URI'))


def build_model(table_name, model_name=None, action='create'):
    if not engine.has_table(table_name):
        print('Table name not found')
        return

    if not model_name:
        pass
    model_name = convert_table_name_to_model(table_name)
    file_name = convert_model_name_to_file_name(model_name)
    file_path = 'database/models/{}.py'.format(file_name)

    inspector = inspect(engine)
    column_infos = inspector.get_columns(table_name)
    new_column_infos = []
    all_type = set(['INTEGER'])
    for column_info in column_infos:
        if column_info['name'] in ('id', 'created_at', 'updated_at'):
            continue
        column_type = column_info['type'].__class__.__name__
        if column_type == 'DOUBLE_PRECISION':
            column_type = 'FLOAT'
        column_info['type_name'] = column_type
        all_type.add(column_type)
        new_column_infos.append(column_info)
    all_type = list(all_type)
    all_type = ', '.join(all_type)

    if os.path.exists(file_path) and action == 'create':
        return
    with open('bin/templates/model_template.py.jinja2') as file_:
        model_template = Template(file_.read())

    model_code = model_template.render(
        all_type=all_type,
        model_name=model_name,
        table_name=table_name,
        column_infos=new_column_infos
    )
    with open(file_path, 'w') as model_file:
        model_file.write(model_code)

    if action == 'create':
        build_service(model_name, file_name)


def build_service(model_name, file_name=None):
    if not file_name:
        file_name = convert_model_name_to_file_name(model_name)
    service_path = 'database/services/{}.py'.format(file_name)

    with open('bin/templates/service_template.py.jinja2') as file_:
        service_template = Template(file_.read())
    service_code = service_template.render(
        model_name=model_name,
        file_name=file_name
    )
    with open(service_path, 'w') as service_file:
        service_file.write(service_code)


def build_crud_view(model_name, write_route=True):
    file_name = convert_model_name_to_file_name(model_name)
    file_path = 'database/models/{}.py'.format(file_name)
    if not os.path.exists(file_path):
        print('Model file not found')
        return
    try:
        exec('from database.models.{} import {}'.format(
            file_name,
            model_name
        ))
    except Exception:
        print('Model not found')
        return

    view_folder = 'apis/{}_api'.format(file_name)
    if not os.path.exists(view_folder):
        os.mkdir(view_folder)

    index_file_name = convert_index_name(file_name)
    index_class_name = convert_file_name_to_model(index_file_name)
    with open('bin/templates/index_template.py.jinja2') as file_:
        index_template = Template(file_.read())
    index_code = index_template.render(
        file_name=file_name,
        model_name=model_name,
        index_class_name=index_class_name
    )
    index_path = '{}/{}.py'.format(view_folder, index_file_name)
    with open(index_path, 'w') as index_file:
        index_file.write(index_code)

    with open('bin/templates/show_template.py.jinja2') as file_:
        show_template = Template(file_.read())
    show_code = show_template.render(
        file_name=file_name,
        model_name=model_name,
        show_class_name=model_name
    )
    show_path = '{}/{}.py'.format(view_folder, file_name)
    with open(show_path, 'w') as show_file:
        show_file.write(show_code)

    if write_route:
        routes_path = 'apis/__init__.py'
        with open('bin/templates/routes_template.py.jinja2') as file_:
            routes_template = Template(file_.read())
        routes_code = routes_template.render(
            folder_name='{}_api'.format(file_name),
            show_file_name=file_name,
            index_file_name=index_file_name,
            show_class_name=model_name,
            index_class_name=index_class_name
        )
        with open(routes_path, 'a') as routes_file:
            routes_file.write(routes_code)


def convert_table_name_to_model(table_name):
    name_split = table_name.split('_')
    name_split[-1] = singularize(name_split[-1])
    file_name = '_'.join(name_split)
    return convert_file_name_to_model(file_name)


def convert_file_name_to_model(file_name):
    name_split = file_name.split('_')
    for index, word in enumerate(name_split):
        name_split[index] = word[0].upper() + word[1:]
    return ''.join(name_split)


def convert_model_name_to_file_name(model_name):
    file_name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', model_name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', file_name).lower()


def convert_index_name(file_name):
    name_split = file_name.split('_')
    name_split[-1] = pluralize(name_split[-1])
    return '_'.join(name_split)


@click.command()
@click.option(
    '-m', '--model_name', type=str, required=True, help='Model name'
)
@click.option(
    '-r', '--write_route', type=bool, required=True, help='Write route option'
)
def build_views(model_name, write_route):
    build_crud_view(model_name, write_route)


if __name__ == '__main__':
    build_views()
