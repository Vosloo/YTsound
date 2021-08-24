#!/usr/bin/env python

from argparse import ArgumentParser

from download import download_url


def add_arguments(parser: ArgumentParser):
    parser.add_argument(
        "-u",
        "--url",
        dest="url",
        required=True,
        type=str,
        help="downloads sounds from video at given url")

    parser.add_argument(
        "-e",
        "--extension",
        dest="ext",
        required=False,
        type=str,
        help="final extension of the file (defaults to mp4)")

    parser.add_argument(
        "-i",
        "--interval",
        dest="interval",
        required=False,
        type=str,
        nargs='+',
        help="""
            crops video to the given time interval [start, end] inclusive
            or in case of only one value given - to the given time [0, end]""")

    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        required=False,
        type=str,
        help="sets custom name for output file (name without extension)")

    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        required=False,
        type=str,
        help="specify output directory (defaults to /home/Music)")


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Script for downloading music from youtube videos.\n")

    add_arguments(parser)

    arguments = parser.parse_args()
    if url := arguments.url:
        ext = arguments.ext
        interval = arguments.interval
        fname = arguments.filename
        output = arguments.output
        download_url(url, ext, interval, fname, output)
