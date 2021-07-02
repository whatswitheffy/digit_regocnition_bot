import numpy as np
import sys          #argv
import os
from scipy.io.wavfile import read, write



def print_with_timeline(data, single_duration, units_name, row_limit):
    for i in range(len(data)):
        if i % row_limit == 0:
            print(f"{single_duration * i:8.3f} {units_name} |  ", end='')
        print(f"{data[i]:.3f} ", end='')
        if (i + 1) % row_limit == 0 or i + 1 == len(data):
            print(f" | {single_duration * (i + 1):8.3f} {units_name}")


def get_segment_energy(data, start, end):
    energy = 0
    data = data / 32768
    for i in range(start, end):
        energy += data[i] * data[i] / (end - start)
    energy = np.sqrt(energy)
    return energy


def get_segments_energy(data, segment_duration):
    segments_energy  = []
    for segment_start in range(0, len(data), segment_duration):
        segment_stop = min(segment_start + segment_duration, len(data))
        energy = get_segment_energy(data, segment_start, segment_stop)
        segments_energy.append(energy)
    return segments_energy


def get_vad_mask(data, threshold):
    vad_mask = np.zeros_like(data)
    for i in range(0, len(data)):
        vad_mask[i] = data[i] > threshold
    return vad_mask


def sec2samples(seconds, sample_rate):
  return int(seconds * sample_rate)


class Segment:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop


def print_segments(segments, single_duration, units_name):
    total_duration = 0.0
    min_duration = 0.0
    max_duration = 0.0
    for i in range(len(segments)):
        start_units = segments[i].start * single_duration
        stop_units = segments[i].stop * single_duration
        duration_units = stop_units - start_units
        total_duration += duration_units
        if i == 0 or min_duration > duration_units:
            min_duration = duration_units
        if i == 0 or max_duration < duration_units:
            max_duration = duration_units
        print(f"{i:5}: {start_units:6.3f} - {stop_units:6.3f} ({duration_units:6.3f} {units_name})")
    print(f"Min   duration: {min_duration:.3f} {units_name}")
    print(f"Mean  duration: {total_duration / len(segments):.3f} {units_name}")
    print(f"Max   duration: {max_duration:.3f} {units_name}")
    print(f"Total segments: {len(segments)}")
    print(f"Total duration: {total_duration:.3f} {units_name}")


def compress_mask(mask):
    segments = [];
    if len(mask) == 0:
        return segments
    start = -1
    stop = -1
    if mask[0] == 1:
        start = 0
    for i in range(len(mask) - 1):
        if mask[i] == 0 and mask[i + 1] == 1:
            start = i + 1;
        if mask[i] == 1 and mask[i + 1] == 0:
            stop = i + 1;
            segments.append(Segment(start, stop));
    if mask[-1] == 1:
        stop = len(mask)
        segments.append(Segment(start, stop));
    return segments

def get_vad_segments(audio, sample_rate, segment_hop_sec, vad_threshold):
    segment_hop_samples = sec2samples(segment_hop_sec, sample_rate)
    segments_energy = get_segments_energy(audio, segment_hop_samples)
    vad_mask = get_vad_mask(segments_energy, vad_threshold)
    segments = compress_mask(vad_mask)
    print_with_timeline(segments_energy, segment_hop_sec , "sec", 10)
    print_with_timeline(vad_mask, segment_hop_sec , "sec", 10)
    print_segments(segments, segment_hop_sec, "sec")
    return segments

def get_digits(wav_file_path):
    fname_wav = wav_file_path.split('/')[-1]
    fname = fname_wav.split('.')[0]
    if start_mode == "-dataset":
        digits = fname.split("_")
    else:
        digits = []
    print(digits)
    return fname, digits

def get_max_duration(segments, sample_rate, segment_hop_sec):
    segment_hop_samples = sec2samples(segment_hop_sec, sample_rate)
    segment_hop_samples = sec2samples(segment_hop_sec, sample_rate)
    max_duration_sec = 0
    for segment in segments:
        duration_sec = (segment.stop - segment.start) * segment_hop_samples / sample_rate
        if duration_sec > max_duration_sec:
            max_duration_sec = duration_sec
    print(max_duration_sec)
    return max_duration_sec

def split_and_save(digits, segments, fname, audio, segment_hop_sec, output_wav_directory, sample_rate):
    segment_hop_samples = sec2samples(segment_hop_sec, sample_rate)
    position = 0
    print(start_mode)
    if start_mode == "-normal":
        print(segments)
        digits = [x for x in range(len(segments))]
    print(segments, digits)
    for digit, segment in zip(digits, segments):
        if start_mode == "-dataset":
            new_wav_file_path = f"{output_wav_directory}/{digit}/{fname}#{position}.wav"
        else:
            new_wav_file_path = f"{output_wav_directory}/{fname}#{position}.wav"

        start_samples = segment.start * segment_hop_samples
        stop_samples = segment.stop * segment_hop_samples
        print("filepath: ")
        print(new_wav_file_path, start_samples, stop_samples)
        write(new_wav_file_path, sample_rate, audio[start_samples:stop_samples])
        position += 1


def process_file(wav_file_path, segment_hop_sec, vad_threshold, output_wav_directory):
    print(wav_file_path)
    sample_rate, audio = read(wav_file_path)
    segments = get_vad_segments(audio, sample_rate, segment_hop_sec, vad_threshold)
    fname, digits = get_digits(wav_file_path)
    if start_mode == "-dataset":
        assert len(digits) == len(segments), "Bad threshold"
    max_duration_sec = get_max_duration(segments, sample_rate, segment_hop_sec)
    assert max_duration_sec <= 0.6, f"max_duration_sec={max_duration_sec:.3f}"
    split_and_save(digits, segments, fname, audio, segment_hop_sec, output_wav_directory, sample_rate)




if __name__ == "__main__":
    argc = len(sys.argv)
    if argc != 6:
        print("Incorrect args. Example:")
        print("python vad.py dataset/wav 0.2 0.015 dataset/splitted/ -dataset")
        exit(1)

    wav_file_path = sys.argv[1]
    segment_hop_sec = float(sys.argv[2])
    vad_threshold = float(sys.argv[3])
    output_wav_directory = sys.argv[4]
    global start_mode
    start_mode = sys.argv[5]
    log = []
    if sys.argv[5] != "-normal" and sys.argv[5] != "-dataset":
        print("Incorrect args. Example:")
        print("python vad.py dataset/wav 0.2 0.015 dataset/splitted/ -dataset")
        exit(1)


    if os.path.isfile(wav_file_path):
        try:
            process_file(wav_file_path, segment_hop_sec, vad_threshold, output_wav_directory)
            log.append(wav_file_path + "\tOK\n")
        except Exception:
            log.append(wav_file_path + "\tFAILED\n")
            exit(1)
    else:
        for file_name in os.listdir(wav_file_path):
            try:
                print(file_name)
                process_file(wav_file_path + file_name, segment_hop_sec, vad_threshold, output_wav_directory)
                log.append(file_name + "\tOK\n")
            except Exception:
                log.append(file_name + "\tFAILED\n")
    with open("log_file.txt", "w") as f:
        log_text = ''.join(log)
        f.write(log_text)