## 8 Pack

8-Pack is a draft simulation tool. Play through the first 8 picks of a draft
(before your old picks influence your new picks), let your friends do the same, and compare!

*Wizzerinus's submission for the Spicerack Hackathon 2024* 

## Development Setup

### Backend

Requires Docker. I recommend that you download
[this file](https://17lands-public.s3.amazonaws.com/analysis_data/draft_data/draft_data_public.MKM.PremierDraft.csv.gz)
if you prefer premier drafts (bo1), or
[this file](https://17lands-public.s3.amazonaws.com/analysis_data/draft_data/draft_data_public.MKM.TradDraft.csv.gz)
if you prefer traditional drafts (bo3).
The `import-drafts` command changes according to the type of draft you chose:
```shell
python -m eightpack.cli import-drafts  # downloaded premier drafts
python -m eightpack.cli import-drafts local-traditional  # downloaded traditional drafts
python -m eightpack.cli import-drafts 17lands-premier  # automatically download premier drafts
python -m eightpack.cli import-drafts 17lands-traditional  # automatically download traditional drafts
```
Note that if you use the 17lands one, you will have to download the file a lot during development
if you mess with the database, I don't recommend that.

```shell
cd backend
pip install requirements.txt
python -m eightpack.cli dev-db
# In a different terminal window:
python -m eightpack.cli import-drafts
python -m eightpack.app  # this starts the webserver, default port 8003
# if you change the port make sure to change the backend URL on the frontend
```

### Frontend

Most functionality requires a running backend.

```shell
cd frontend
npm install
npm run dev  # this starts the webserver, default port 5173
# if you change the port make sure to change the CORS header sent by the backend
```

## Production setup

```shell
# this starts the servers
docker-compose up
# this creates the database and imports the drafts, change 17lands-traditional to 17lands-premier if you prefer these
docker exec -it $(docker container ls | grep 8-pack | grep backend | awk '{print $1}') \
  python -m eightpack.cli import-drafts 17lands-traditional \
  'postgresql+psycopg2://user:password@postgres/8pack'
```
