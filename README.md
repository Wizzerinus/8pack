## 8 Pack

8-Pack is a draft simulation tool. Play through the first 8 picks of a draft
(before your old picks influence your new picks), let your friends do the same, and compare!

*Wizzerinus's submission for the Spicerack Hackathon 2024* 

## Development Setup

### Backend

Requires Docker. Also currently requires that you download
[this file](https://17lands-public.s3.amazonaws.com/analysis_data/draft_data/draft_data_public.MKM.PremierDraft.csv.gz)
from 17lands and put it into the project root (will be amended later).

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

(WIP)
