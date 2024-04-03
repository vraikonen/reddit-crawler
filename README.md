<a name="readme-top"></a>


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://git.sbg.ac.at/geo-social-analytics/geo-social-media/telegram-crawler">
    <img src="img/icon.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Reddit Historical Crawler</h3>

  <p align="center">
    Offical Reddit API exists, it has a free tier (that is enough to crawl all the posts/comments in present), but it also has many drawbacks when it comes to fetching historical data. In that regard, this script utilizes existing reddit dumps (archives) to go back in time and filter the dump for the desired posts. It stores posts (submissions) and comments in the database. Then, it uses official API to crawl the filtered posts based on their ID, thus provding another updated dataset of posts and comments.
    <br />
    <a href="https://git.sbg.ac.at/geo-social-analytics/geo-social-media/reddit-crawler"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://git.sbg.ac.at/geo-social-analytics/geo-social-media/reddit-crawler">View Demo</a>
    ·
    <a href="https://git.sbg.ac.at/geo-social-analytics/geo-social-media/reddit-crawler/-/issues">Report Bug</a>
    ·
    <a href="https://git.sbg.ac.at/geo-social-analytics/geo-social-media/reddit-crawler/-/issues">Request Feature</a>
  </p>
</div>


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

- python == 3.12.2
- praw == 7.7.1
- prawcore == 2.4.0
- pymongo == 4.6.2
- zstandard == 0.22.0

> **__Note:__** As we are using Reddit API, probably in the future you will need to install newer version of praw, so you can install latest stable python realease and install packages without specifying the version.
### Step 1: Set-up repo

1. Clone the repo.

2. Create a Python environment.

3. Install `requirements.txt` and (potentially) remove package version number.
```
pip install -r requirements.txt
```
### Step 2: Find Reddit dump

1. Find a link to an archive (dump) coresponding to the month you are interested in [here](https://github.com/ArthurHeitmann/arctic_shift/releases) prefereably, or where ever you can find a dump. I tried with two different dumps from two different sources, and this code works. I cannot be sure if it will work with every Reddit dump.

2. Download submissions and comments archives for the desired month. You will need to do it via any torrent app.

### Step 3: Dump query configuration

1. Open file `config/query-params.ini`. There are option to query dump based on 
  - keyword found in the title and the text of the submission, 
  - author, 
  - subreddit and 
  - start and end date. 
  
> **__Note:__** Besides start and end date, all conditions are connected with an OR statement, therefore if at least one condition is True, submission will be retrieved from the dump. 

2. Lastly, provide the path to the comments and submissions you downloaded from the Reddit archive by filling the `file_path_sub` `file_path_com`. 

3. Example config is provided.

> **__Note:__** Config file `config/query-params.ini` has comments with guidelines on how to define a query. If you want to filter based on other query attributes, open an issue [here](https://git.sbg.ac.at/geo-social-analytics/geo-social-media/telegram-crawler/-/issues). 

### Step 4: Obtain Reddit API credentials

1. Refer to any tutorial online and get Reddit API credentials. 

2. Fill in the config file `config/config-reddit-api.ini` with client_id, client_secret, password, username and user_agent. Config has a further explanation on how to fill this. 

3. Decide on attributes you want to retrieve for submissions and comments. Each attribute is a separate API call. So in order to make this faster, open database with filtered submissions from the dump, explore attributes and choose the ones you need. File `config/config-reddit-api.ini` has an example and more explanation. 

### Step 5: Database configuration

#### Option 1 - Recommended Database configuration with .msi installer
1. Visit the [MongoDB download page](https://www.mongodb.com/try/download/community) and download Community Server. 

2. The easiest installation is through Windows installer (msi package), by selecting the "Run Service as Network Service user" option when prompted during the installation process.

3. Optionally, change path to the logs and data folders during the installation.

4. Navigate to the `config` folder and modify the `config-db.ini` file. Update the `server_path` (default port: 27017, or adjust it in `bin/mongo.cfg` within the MongoDB installation folder) along with the database and collection names.

5. Optionally, but no need for that, change the database name and the collection name. Check [naming restrictions for MongoDB](https://www.mongodb.com/docs/manual/reference/limits/?_ga=2.67582801.1990405345.1706732504-2064098827.1705526269#naming-restrictions).

#### Option 2: Alternative Database configuration with MongoDB binaries (Windows)
Since the Windows .msi distribution needs be installed on the system drive, here are the steps for installing MongoDB binaries which can be installed on the data disk.

1. Visit the [MongoDB download page](https://www.mongodb.com/try/download/community) and choose MongoDB binaries (zip package).

2. Extract the downloaded archive to a location of your choice.

3. Create the following folders at the location of your choice and use them in the next step: 
  - `log` for logging performance of the database and 
  - `data` to store actual data.

4. Launch the command prompt with **administrator privileges**, navigate to the `bin` folder in the directory of extracted MongoDB binaries, and run the following commands to create Windows Service (adjust the paths to `log` and `data` according to your system location):
    ```bash
    mongod --repair 

    mongod --remove 

    mongod --bind_ip  127.0.0.1  --logpath  E:/MongoDBbin/log/mongod.log  --logappend  --dbpath  E:/MongoDBbin/data/db  --port 27017 --serviceName "MongoDB-bin" --serviceDisplayName "MongoDB-bin" --install

    net start MongoDB-b
    ```

5. Check [MongoDB configuration options](https://www.mongodb.com/docs/manual/reference/configuration-options/) to understand the arguments. 

6. Now you can adjust MongoDB service preferences through the Windows Services application.

    > **Note:** This set up of MongoDB binaries excludes an option to configure the port to the server and the path to the data directory in the file `bin/mongo.cfg`, as all configurations have been set through the preceding commands.

7. To finish setting up MongoDB, follow the steps 5 and 6 outlined in the earlier section "Database Configuration (Windows .msi)". 

### Step 6: Run the script 

1. Run the `main_dump.py`. Keep track of its progress in the log file `applicationMain.log`.
    ```
    python main_dump.py
    ```
2. After the first script is finished, run the `main_api.py` script.
    ```
    python main_api.py
    ```
<!-- Restart of the script -->
## Restart of the script
Do not terminate filtering of the dump, i.e. `main_dump.py`, as this script does not keep track of the processed submissions/comments.
The reason for this is that this script has no long lasting API calls, thus just do not turn of your computer for an hour or two - depending on the complexity of your qwery. On the other hand, you can terminate `main_api.py`. After you restart this script, it will continue where it stopped, assuming we could sometime query API for many days.

<!-- Database overview -->
## Database overview
Finally, after all the previous steps, you have two datasets of comments and and two datasets of posts, stored in 4 collections. Collections ``submissions_dump`` and ``comments_dump`` have reddit posts and comments with the content that existed when the dump was created. Collections ``comments_API`` and ``submissions_API`` have the content that exist on the date when the script accesses Reddit API. There is also another collection named ``failed_API_retireval`` that stores all the submissions that could not be accessed, as well as a reason for that (error returned from the API).


<!-- Suggestions and Issues -->
## Feature Requests and Bug Reports

See the [open issues](https://git.sbg.ac.at/geo-social-analytics/geo-social-media/reddit-crawler/-/issues) for a full list of proposed features and known issues.

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []() Nefta Kanilmaz Umut

<p align="right">(<a href="#readme-top">back to top</a>)</p>
