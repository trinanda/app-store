import datetime
import os
import shutil

from flask_apscheduler import APScheduler
from pygdrive3 import service

scheduler = APScheduler()


def backup_db_to_google_drive():
    dir_path = os.path.dirname(os.path.realpath('../config.py')) + '/AQUR/'
    drive_service = service.DriveService(dir_path + 'credentials/client_secret.json')
    try:
        drive_service.auth()
    except Exception as e:
        return str(e)

    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    filename_to_upload = 'aqur_database_' + current_time

    # backup database | https://github.com/cuducos/alchemydumps#you-can-backup-all-your-data
    os.system('python3 manage.py alchemydumps create')

    folder_name_on_local = 'alchemydumps-backup'
    # convert directory to zip
    file_to_upload = shutil.make_archive(dir_path + 'save_db_bak/' + filename_to_upload, 'zip',
                                         dir_path + folder_name_on_local)

    # folder name on google drive
    folder = drive_service.create_folder('aqur_db_backup_' + current_time)

    # # upload file (args1=filename_to_upload, args2=file_to_upload, args3=directory_name)
    try:
        file = drive_service.upload_file(filename_to_upload, file_to_upload, folder)
        print('uploaded to to google drive', file)
    except Exception as e:
        return str(e)

    root_password = os.environ.get('SUDO')
    os.system('echo ' + root_password + '| sudo -S rm -rf alchemydumps-backup/*')
    print('Deleted the database backup on local ' + folder_name_on_local + ' folder')

    return file
