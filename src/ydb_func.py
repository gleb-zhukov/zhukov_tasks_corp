import ydb
import ydb.iam
import os

# Create driver in global space.
driver = ydb.Driver(
  endpoint='xxx',
  database='xxx',
  credentials=ydb.AccessTokenCredentials('xxx') #remove in YC
  #credentials=ydb.iam.MetadataUrlCredentials() #use in YC
)
# Wait for the driver to become active for requests.
driver.wait(fail_fast=True, timeout=5)
session = driver.table_client.session().create()

def ydb_get_projects_by_user_id(user_id):
    ydb_request = f'SELECT projects.project_name, projects.id from users JOIN projects_users ON users.id = projects_users.user_id JOIN projects ON projects.id = projects_users.project_id where users.id = {user_id}'
    result_sets = session.transaction().execute(ydb_request, commit_tx=True)
    project_name = list()
    project_id = list()
    for row in result_sets[0].rows:
        project_name.append(row['projects.project_name']) 
        project_id.append(row['projects.id'])
    return project_id, project_name


def ydb_get_tasks_by_status_project_and_executor(task_executor_id, task_status, task_project_id):
    ydb_request = f'SELECT id, task_header FROM tasks WHERE task_project_id = "{task_project_id}" AND task_executor_id = {task_executor_id} AND task_status = "{task_status}"'
    result_sets = session.transaction().execute(ydb_request, commit_tx=True)
    task_id = list()
    task_header = list()
    for row in result_sets[0].rows:
        task_id.append(row['id']) 
        task_header.append(row['task_header'])
    return task_id, task_header

def ydb_get_tasks_by_status_project_and_owner(task_owner_id, task_status, task_project_id):
    ydb_request = f'SELECT id, task_header FROM tasks WHERE task_project_id = "{task_project_id}" AND task_owner_id = {task_owner_id} AND task_status = "{task_status}"'
    result_sets = session.transaction().execute(ydb_request, commit_tx=True)
    task_id = list()
    task_header = list()
    for row in result_sets[0].rows:
        task_id.append(row['id']) 
        task_header.append(row['task_header'])
    return task_id, task_header


def ydb_get_projects_by_owner_id(user_id):
    ydb_request = f'SELECT project_name, id from projects where project_owner_id = {user_id}'
    result_sets = session.transaction().execute(ydb_request, commit_tx=True)
    project_name = list()
    project_id = list()
    for row in result_sets[0].rows:
        project_name.append(row.project_name)
        project_id.append(row.id)
    return project_id, project_name

def ydb_get_project_data(project_id):
    ydb_request = f'select project_name, project_owner_id from projects where id == "{project_id}"'
    result_sets = session.transaction().execute(ydb_request, commit_tx=True)
    for row in result_sets[0].rows:
        project_name = row.project_name
        project_owner_id = row.project_owner_id
        return project_name, project_owner_id
    
def ydb_get_user_data(user_id):
    ydb_request = f'select user_task_id, user_full_name, user_role, user_create_task_flag from users where id == {user_id}'
    result_sets = session.transaction().execute(ydb_request, commit_tx=True)
    for row in result_sets[0].rows:
        user_task_id = row.user_task_id
        user_full_name = row.user_full_name
        user_role = row.user_role
        user_create_task_flag = row.user_create_task_flag
        return user_task_id, user_full_name, user_role, user_create_task_flag

def ydb_get_task_data(task_id, **data):
    
    ydb_request = 'SELECT '
    for key, value in data.items():
        if value == True:
            ydb_request = ydb_request + str(key) + ', '

    # убираем последнюю запятую
    str_len = len(ydb_request)
    ydb_request = ydb_request[:str_len-2] + ' ' + ydb_request[str_len:] + f'FROM tasks WHERE id == "{task_id}"'

    result_sets = session.transaction().execute(ydb_request, commit_tx=True)

    result = list()
    for row in result_sets[0].rows:
        result.append(row)
    return result


def ydb_update_task_data(task_id, task_header = None, task_body = None, task_owner_id = None, task_executor_id = None, task_project_id = None, task_status = None, task_urgent_flag = None,  task_deadline = None):

    ydb_request = 'upsert into tasks (id'
    if task_header != None:
        ydb_request = ydb_request + ',task_header'
    if task_body != None:
        ydb_request = ydb_request + ',task_body'
    if task_owner_id != None:
        ydb_request = ydb_request + ',task_owner_id'
    if task_executor_id != None:
        ydb_request = ydb_request + ',task_executor_id'
    if task_project_id != None:
        ydb_request = ydb_request + ',task_project_id'
    if task_status != None:
        ydb_request = ydb_request + ',task_status'
    if task_urgent_flag != None:
        ydb_request = ydb_request + ',task_urgent_flag'
    if task_deadline != None:
        ydb_request = ydb_request + ',task_deadline'

    ydb_request = ydb_request + f') values ("{task_id}"'

    if task_header != None:
        ydb_request = ydb_request + f',"{task_header}"'
    if task_body != None:
        ydb_request = ydb_request + f',"{task_body}"'
    if task_owner_id != None:
        ydb_request = ydb_request + f',{task_owner_id}'
    if task_executor_id != None:
        ydb_request = ydb_request + f',{task_executor_id}'
    if task_project_id != None:
        ydb_request = ydb_request + f',"{task_project_id}"'
    if task_status != None:
        ydb_request = ydb_request + f',"{task_status}"'
    if task_urgent_flag != None:
        ydb_request = ydb_request + f',{task_urgent_flag}'
    if task_deadline != None:
        ydb_request = ydb_request + f',"{task_deadline}"'
    ydb_request = ydb_request + ')'

    session.transaction().execute(ydb_request, commit_tx=True)

    return

def ydb_update_user_data(user_id, user_task_id = None, user_full_name = None, user_role = None, user_create_task_flag = None):
    
    ydb_request = 'upsert into users (id'
    if user_task_id != None:
        ydb_request = ydb_request + ',user_task_id'
    if user_full_name != None:
        ydb_request = ydb_request + ',user_full_name'
    if user_role != None:
        ydb_request = ydb_request + ',user_role'
    if user_create_task_flag != None:
        ydb_request = ydb_request + ',user_create_task_flag'

    ydb_request = ydb_request + f') values ({user_id}'

    if user_task_id != None:
        ydb_request = ydb_request + f',"{user_task_id}"'
    if user_full_name != None:
        ydb_request = ydb_request + f',"{user_full_name}"'
    if user_role != None:
        ydb_request = ydb_request + f',"{user_role}"'
    if user_create_task_flag != None:
        ydb_request = ydb_request + f',{user_create_task_flag}'

    ydb_request = ydb_request + ')'

    session.transaction().execute(ydb_request, commit_tx=True)
    return
