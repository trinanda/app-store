# App-Store

This app based on this nicely boilerplate: https://github.com/hack4impact/flask-base

## What's included?

* Adminator dashboard template
* Chart.js
* DataTables
* Blueprints
* User and permissions management
* Flask-SQLAlchemy for databases
* Flask-WTF for forms
* Flask-Assets for asset management and SCSS compilation
* Flask-Mail for sending emails
* gzip compression
* Redis Queue for handling asynchronous tasks
* ZXCVBN password strength checker
* CKEditor for editing pages
* Error handling | log files and send stacktrace to email
* i18n and L10n
* APScheduler
* AlchemyDumps | autobackup database to google drive every days
* and other features that we can see from the packages that we use on requirements.txt

## Setting up

##### Clone the repository 

```
$ git clone https://github.com/trinanda/app-store.git
$ cd app-store/
```

##### Initialize a virtual environment

Windows:
```
$ python3 -m venv venv
$ venv\Scripts\activate.bat
```

Unix/MacOS:
```
$ python3 -m venv venv
$ source venv/bin/activate
```
Learn more in [the documentation](https://docs.python.org/3/library/venv.html#creating-virtual-environments).

Note: if you are using a python before 3.3, it doesn't come with venv. Install [virtualenv](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv) with pip instead.

##### (If you're on a Mac) Make sure xcode tools are installed

```
$ xcode-select --install
```

##### Add Environment Variables

Create a file called `.env` that contains environment variables. **Very important: do not include the `.env` file in any commits. This should remain private.** You will manually maintain this file locally, and keep it in sync on your host.

Variables declared in file have the following format: `ENVIRONMENT_VARIABLE=value`. You may also wrap values in double quotes like `ENVIRONMENT_VARIABLE="value with spaces"`.

1. In order for Flask to run, there must be a `SECRET_KEY` variable declared. Generating one is simple with Python 3:

   ```
   $ python3 -c "import secrets; print(secrets.token_hex(16))"
   ```

   This will give you a 32-character string. Copy this string and add it to your `.env`:

   ```
   SECRET_KEY=Generated_Random_String
   ```

2. The mailing environment variables can be set as the following.

   ```
   MAIL_USERNAME=SendgridUsername
   MAIL_PASSWORD=SendgridPassword
   ```

Other useful variables include:

| Variable        | Default/example   | Description  |
| --------------- |-------------| -----|
| `ADMIN_EMAIL`   | `your_admin_email@example.com` | Email for your first admin account |
| `ADMIN_PASSWORD`| `password12345` | Password for your first admin account |
| `DATABASE_URL`  | `data-dev.sqlite` | Database URL. Can be Postgres, sqlite, etc. |
| `DEV_DATABASE_URL`| `postgresql://username:password@localhost/dbname` | Database URL for development |
| `REDISTOGO_URL` | `http://localhost:6379` | [Redis To Go](https://redistogo.com) URL or any redis server url |
| `RAYGUN_APIKEY` | `None` | API key for [Raygun](https://raygun.com/raygun-providers/python), a crash and performance monitoring service |
| `FLASK_CONFIG`  | `default` | can be `development`, `production`, `default`, `heroku`, `unix`, or `testing`. Most of the time you will use `development` or `production`. |
| `ALCHEMYDUMPS_FTP_SERVER`| `partnerupload.google.com` | Alchemy dumps FTP Server |
| `ALCHEMYDUMPS_FTP_USER`| `your_drive_email@example.com` | Alchemy dumps FTP User |
| `ALCHEMYDUMPS_FTP_PASSWORD`| `password12345` | Alchemy dumps FTP Password |
| `ALCHEMYDUMPS_FTP_PATH`| `/absolute/path/` | Alchemy dumps FTP Path |
| `MAIL_USERNAME`| `your_email@example.com` | This will be used as the main email, such as sending a stack trace, invite users, etc.. |
| `MAIL_PASSWORD`| `password12345` | Mail password |
| `MAIL_SERVER`| `smtp_server` | Mail SMTP server, eg: `smtp.googlemail.com` if we use google SMTP server |
| `MAIL_PORT`| `587` | Mail port |
| `MAIL_USE_TLS`| `1` | mail use TLS |
| `ADMINS`| `admin_email1_for_stacktrace_alert@example.com, admin_email2_for_stacktrace_alert@example.com, admin_email3_for_stacktrace_alert@example.com, etc..` | Admin email for logging / stacktrace | please don't wrap the email with marking quote |
| `SECRET_KEY`| `Generated_Random_String` | Flask secret key |
| `APP_NAME`| `"MY APP"` | Application name wraps with double-quote if contain spaces |
| `HOST`| `0.0.0.0` | Server host |
| `PORT`| `8000` | Server port |
| `SSL_DISABLE`| `True` | SSL |
| `GOOGLE_ANALYTICS_ID`| `your_google_analytics_id` | Google analytics ID |
| `SUDO`| `sudo_password` | sudo access |

##### Install the dependencies

```
$ pip install -r requirements.txt
```

##### Other dependencies for running locally

You need [Redis](http://redis.io/), and [Sass](http://sass-lang.com/). Chances are, these commands will work:


**Sass:**

```
$ gem install sass
```

**Redis:**

_Mac (using [homebrew](http://brew.sh/)):_

```
$ brew install redis
```

_Linux:_

```
$ sudo apt-get install redis-server
```

You will also need to install **PostgresQL**

_Mac (using homebrew):_

```
brew install postgresql
```

_Linux (based on this [issue](https://github.com/hack4impact/flask-base/issues/96)):_

```
sudo apt-get install libpq-dev
```


##### Create the database

```
$ python manage.py recreate_db
```

##### Other setup (e.g. creating roles in database)

```
$ python manage.py setup_dev
```

Note that this will create an admin user with email and password specified by the `ADMIN_EMAIL` and `ADMIN_PASSWORD` config variables. If not specified, they are both `appstore@gmail.com` and `password` respectively.

##### [Optional] Add fake data to the database

```
$ python manage.py add_fake_data
```

## Running the app

```
$ source env/bin/activate
$ honcho start -e config.env -f Local
```

For Windows users having issues with binding to a redis port locally, refer to [this issue](https://github.com/hack4impact/flask-base/issues/132).

## Formatting code

Before you submit changes to flask-base, you may want to autoformat your code with `python manage.py format`.

## License
[MIT License](LICENSE.md)
