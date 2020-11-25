from pytube import YouTube 
from pathlib import Path
import subprocess


def _check_interval(interval: list):
    """Validates the interval and then returns it formatted"""
    if len(interval) > 2:
        raise Exception("Too many arguments!")

    start = ""
    end = ""
    for ind, item in enumerate(interval):
        side: str = item.split(':')
        if len(side) > 2:
            raise Exception("Invalid time interval!")

        if not all([val.isnumeric() for val in side]):
            raise Exception("Invalid time interval!")

        side_len = len(side)
        if ind == 0:
            if side_len == 1:
                start = side[0] + ":0"
            else:
                if len(side[1]) == 1:
                    # Adding trailing zero
                    side[1] = side[1] + '0'
                start = ":".join(side)
        else:
            if side_len == 1:
                end = side[0] + ":0"
            else:
                if len(side[1]) == 1:
                    # Adding trailing zero
                    side[1] = side[1] + '0'
                end = ":".join(side)

    return (start, end)


def _get_new_length(video_len: int, left: str, right: str):
    """Returns length of cropped video"""
    left_time, right_time = -1, -1 # Only for supressing warnings

    if left:
        minutes, secods = list(map(int, left.split(':')))
        left_time = minutes * 60 + secods
        if left_time > video_len:
            raise Exception("Start of the cropped video exceeds video length!")

    if right:
        minutes, secods = list(map(int, right.split(':')))
        right_time = minutes * 60 + secods
        if right_time > video_len:
            raise Exception("End of the cropped video exceeds video length!")

    if left and right:
        if left_time > right_time:
            raise Exception("Start of the interval is bigger than the end!")

        new_minutes = str((right_time - left_time) // 60)
        new_seconds = str((right_time - left_time) % 60)
        return ":".join([new_minutes, new_seconds])
    else:
        # Only cropped from start (only left time)
        new_minutes = str((video_len - left_time) // 60)
        new_seconds = str((video_len - left_time) % 60)
        return ":".join([new_minutes, new_seconds])


def download_url(url: str, interval: list, fname: str, output: str):
    """Downloads music from given url with a given time interval"""
    try:
        yt = YouTube(url)
    except Exception:
        print("Invalid url!")
        return

    best_audio = yt.streams.filter(only_audio=True).first()

    if not best_audio.includes_audio_track:
        print(
            f"Unfortunately video: \"{yt.title}\" does not contain audio track!"
        )
        return

    video_len = yt.length
    if interval is not None:
        try:
            left, right = _check_interval(interval)
            new_length = _get_new_length(video_len, left, right)
        except Exception as exc:
            print(exc.args[0])
            return
    else:
        left, right = ('', '')
        new_length = f"{video_len // 60}:{video_len % 60}"

    if fname is None:
        fname = best_audio.default_filename.split('.')[0]

    if output is None:
        output = str(Path.home()) + '/Music/'

    filename = best_audio.download(output_path=output, filename=fname)

    cp_file = filename.split('.')
    cp_file = cp_file[0] + "_cp." + cp_file[1]

    start = f"-ss {left}" if left != '' else ''
    end = f"-to {right}" if right != '' else ''

    crop_cmd = f"ffmpeg -loglevel warning {start} {end} -i \"{filename}\" -codec copy \"{cp_file}\""
    subprocess.run(crop_cmd, shell=True)

    mv_cmd = f"rm \"{filename}\"; mv \"{cp_file}\" \"{filename}\""
    subprocess.run(mv_cmd, shell=True)

    print(f"File saved in: {filename}")
    print(f"Music duration: {new_length}")
