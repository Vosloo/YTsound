#!/usr/bin/env python

import subprocess
from pathlib import Path
from typing import Tuple

from pytube import YouTube


def _format_time(side) -> str:
    if len(side) == 1:
        if len(side[0]) == 1:
            # mins < 10; add leading zero
            limit = f"0{side[0]}"
        limit += ":00"
    else:
        mins, secs = side
        # Adding leading / trailing zero
        if len(mins) == 1:
            mins = "0" + mins
        if len(secs) == 1:
            secs = secs + "0"
        limit = ":".join([mins, secs])

    return limit


def _check_interval(interval: list) -> Tuple[str, str]:
    """Validates the interval and then returns it formatted"""
    if len(interval) > 2:
        raise Exception("Too many arguments!")

    limits = []
    for item in interval:
        side: str = item.split(':')
        if len(side) > 2:
            raise Exception("Invalid time interval!")

        if not all([val.isnumeric() for val in side]):
            raise Exception("Invalid time interval!")

        limits.append(_format_time(side))

    if len(limits) == 2:
        start, end = limits
    else:
        start, end = "", *limits

    return (start, end)


def _get_new_length(video_len: int, left: str, right: str):
    """Returns length of cropped video"""
    left_time, right_time = -1, -1  # Only for supressing warnings

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

        mins = (right_time - left_time) // 60
        secs = (right_time - left_time) % 60
    else:
        # Only cropped to the given timestamp (only right time)
        mins = right_time // 60
        secs = right_time % 60

    zeros_m = "0" if mins < 10 else ""
    zeros_s = "0" if secs < 10 else ""

    return ":".join([f"{zeros_m}{mins}", f"{zeros_s}{secs}"])


def download_url(url: str, final_ext: str, interval: list, fname: str, output: str):
    """Downloads music from given url with a given time interval"""
    try:
        yt = YouTube(url)
    except Exception:
        print("Invalid url!")
        return

    best_audio = yt.streams.filter(
        only_audio=True, file_extension='mp4').first()

    if not best_audio.includes_audio_track:
        print(
            f"Unfortunately video: \"{yt.title}\" does not contain audio track!")
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
        zeros_s = "0" if (video_len % 60) < 10 else ""
        zeros_m = "0" if (video_len // 60) < 10 else ""
        new_length = f"{zeros_m}{video_len // 60}:{zeros_s}{video_len % 60}"

    if fname is None:
        fname, original_ext = best_audio.default_filename.split('.')
    elif '.' in fname:
        # Filename with extension
        fname, original_ext = fname.split('.')
    else:
        # Filename stem (no extension)
        fname, original_ext = fname, 'mp4'

    if output is None:
        output = str(Path.home()) + '/Music/'

    print("Downloading music...")
    filename = best_audio.download(output_path=output, filename=fname)
    cp_file = None

    if final_ext is None:
        final_ext = original_ext

    if interval is not None:
        start = f"-ss {left}" if left else ""
        end = f"-to {right}" if right else ""

        print_left = left if left else "00:00"
        print(f"Cropping music with interval: {print_left} - {right}")

        cp_file = filename + "_cp." + original_ext

        # Cannot be done in place so copy must be done
        crop_cmd = f"ffmpeg -loglevel warning {start} {end} -i \"{filename}\" -codec copy \"{cp_file}\"; rm \"{filename}\""
        subprocess.run(crop_cmd, shell=True)

    if cp_file is None:
        # No copy was created
        cp_file = filename

    print("Saving music in desired format...")
    mv_cmd = f"ffmpeg -loglevel warning -i \"{cp_file}\" \"{filename}.{final_ext}\""
    rm_cmd = f"rm \"{cp_file}\""

    mv_output = subprocess.run(mv_cmd, shell=True)
    subprocess.run(rm_cmd, shell=True)

    if mv_output.returncode == 0:
        print(f"File saved in: {filename}")
        print(f"Music duration: {new_length}")


if __name__ == '__main__':
    print("Please run ytsound script!")
