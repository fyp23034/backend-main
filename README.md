# Backend for FYP23034

## Before running the app
Get a `.env` file from [@BrandonTay2001](https://github.com/BrandonTay2001) and place it in the root directory of this repo

## Running the app 
```
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python app.py
```

## API and Database Documentation:
Refer to: https://connecthkuhk-my.sharepoint.com/:x:/g/personal/sabcyt02_connect_hku_hk/Edf_rzZ7CFdJq0BUyyQL1PcBymbs1tUBjM9A2t_wjPX5_A?e=p8Cljx 

### OR...
The /docs folder in this repo

### Common Problems
1. OSError: [E053] Could not read config file from .../miniconda3/lib/python3.11/site-packages/en_core_web_sm/en_core_web_sm-2.2.0/config.cfg
   --> please refer to https://stackoverflow.com/questions/76321221/error-importerror-cannot-import-name-get-object-size-from-bson
