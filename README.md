# video-to-clip
A python program to create clips for reels/shorts/tiktok from a youtube video.

## Getting started

### Create a new python env
```
python3 -m venv .venv
```

### Install all dependencies
```
pip3 install -r requirements.txt
```

## Usage
To starting the process you just need to active the new python env and run `main.py` file providing a youtube video id:

```
source ./.venv/bin/activate
```

```
python3 main.py --video [YOUTUBE_VIDEO_ID]
```

By default the program will create a root folder based on youtube id at your home directory, you can override all default settings using command line arguments. 

```
python3 main.py --help
```

You'll see all argument options
