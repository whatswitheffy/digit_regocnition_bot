import os 
from numpy.lib.utils import source
import subprocess

if __name__ == "__main__":
    source = "dataset/ogg1/"
    files = os.listdir(source)
    number_of_files = len(files)
    for i in range(number_of_files):
        current_file = files[i]
        destination = "dataset/wav1/" + current_file[:-4] + ".wav"                                       
        subprocess.call(["ffmpeg", "-y", "-i", source + current_file, destination])
