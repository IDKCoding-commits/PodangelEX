import os
import json
import re
import signal
import subprocess
import tempfile
from collections import namedtuple
from pathlib import Path

import whisper_timestamped
from detoxify import Detoxify
import multiprocessing

worker_model = None
global_pool = None
shutdown_in_progress = False
detox_model = None

WordToMute = namedtuple('WordToMute', ['word', 'start', 'end'])
SegmentToMute = namedtuple('SegmentToMute', ['start', 'end'])

def read_config(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return config_menu() or {}

def read_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def write_config(file_path, content):
    try:
        with open(file_path, 'w') as outfile:
            json.dump(content, outfile, indent=4, sort_keys=True)
    except FileNotFoundError:
        print("Config not found")

def size_finder(size_input: str, config_dict: dict) -> int | str:
    models = {
        "1": ("tiny", 1),
        "2": ("base", 1),
        "3": ("small", 2),
        "4": ("medium", 5),
        "5": ("large", 10),
        "6": ("turbo", 6),
    }
    
    key = size_input.lower().strip()
    if key not in models:
        print("Please select a valid number")
        return "F"
    
    model_name, vram_cost = models[key]
    config_dict["model_size"] = model_name
    write_config("./config.json", config_dict)
    return vram_cost

def category_finder(input_str: str, config_dict: dict, value: float) -> None:
    valid_categories = {"t", "st", "th", "o", "id", "i"}
    key = input_str.lower().strip()
    
    if key not in valid_categories:
        print("Please select a valid category")
        return
    
    config_dict[key] = value
    write_config("./config.json", config_dict)

def severity_tweaker(input_str: str, config_dict: dict) -> None:
    try:
        category, value = input_str.split("-")
        float_value = float(value)
        
        if not 0 <= float_value <= 1:
            print("Number must be between 0 and 1")
            return
        
        category_finder(category, config_dict, float_value)
    except (ValueError, IndexError):
        print("Invalid format. Use: category-value (e.g., st-0.5)")

def config_menu() -> None:
    config_data = {
        "file_path": "./",
        "worker_count": "1",
        "model_size": "small",
        "t": 0.5, "st": 0.5, "o": 0.5, "th": 0.5, "i": 0.5, "id": 0.5
    }
    
    try:
        with open("config.json", 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        pass
    
    print("\n\nSelect model size:\n 1: tiny (1GB)\n 2: base (1GB)\n 3: small (2GB)\n"
          " 4: medium (5GB)\n 5: large (10GB)\n 6: turbo (6GB)")
    while True:
        model_size = input("\nInput a number: ")
        vram_cost = size_finder(model_size, config_data)
        if vram_cost != "F":
            break
    
    if input("\nChange file paths from default? (y/N): ").lower().strip() == "y":
        new_dir = input("Enter path: ").strip()
    else:
        new_dir = "./"
    config_data["file_path"] = new_dir
    write_config("./config.json", config_data)
    
    while True:
        try:
            worker_count = input("\nNumber of workers: ").strip()
            int_count = int(worker_count)
            vram_total = int_count * vram_cost
            if input(f"\nWarning: Uses {vram_total}GB VRAM. Continue? (Y/n): ").lower().strip() != "n":
                config_data["worker_count"] = worker_count
                write_config("./config.json", config_data)
                break
        except ValueError:
            print("Please enter a valid number")
    
    if input("\nConfigure toxicity thresholds? (y/N): ").lower().strip() == "y":
        print("\nSet thresholds (category-value, e.g., st-0.5):\n"
              "t=toxicity, st=severe, o=obscene, th=threats, i=insults, id=identity")
        while True:
            severity_tweaker(input("Enter setting (or press Enter to skip): "), config_data)
            if input("Continue? (y/N): ").lower().strip() != "y":
                break
    
    for subdir in ['Input', 'Output', '.bridge']:
        os.makedirs(os.path.join(new_dir, subdir), exist_ok=True)
    
    print("\nConfiguration complete!")

def get_audio_duration(file_path: str) -> float | None:
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        print(f"Error getting audio duration for {file_path}")
        return None

def worker_initializer(model_size: str) -> None:
    global worker_model
    worker_model = whisper_timestamped.load_model(model_size)

def process_file(filename: str, input_path: str) -> dict:

    global worker_model
    file_path = os.path.join(input_path, filename)
    transcribed_file = whisper_timestamped.transcribe(worker_model, file_path)
    print(f"Transcribed: {filename}")
    return transcribed_file

def cleanup_workers() -> None:

    global global_pool
    if global_pool:
        print("Shutting down worker pool...")
        global_pool.terminate()
        global_pool.join()
        global_pool = None

def signal_handler(signum, frame):
    global shutdown_in_progress
    if shutdown_in_progress:
        return
    shutdown_in_progress = True
    print(f"\nReceived signal {signum}, shutting down...")
    cleanup_workers()
    exit()

signal.signal(signal.SIGINT, signal_handler)

def clean_text(text: str, words_to_remove: list) -> str:
    cleaned = text
    for word in words_to_remove:
        cleaned = re.sub(rf'\b{re.escape(word)}\b', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()

def audio_cleaner(transcribed_file: dict, bad_words: dict, thresholds: list) -> tuple:
    words_to_mute = []
    segments_to_mute = []
    swear_words = {s.lower() for s in bad_words.get('swears', [])}
    

    for segment in transcribed_file.get('segments', []):
        for word in segment.get('words', []):
            word_text = word.get('text', '').lower().strip('.,!?')
            if word_text in swear_words:
                words_to_mute.append(WordToMute(
                    word['text'],
                    float(word['start']),
                    float(word['end'])
                ))
    

    global detox_model
    if detox_model is None:
        print("Warning: detox_model not initialized")
        return words_to_mute, segments_to_mute
    
    swear_set = {m.word.lower().strip('.,!?') for m in words_to_mute}
    
    for segment in transcribed_file.get('segments', []):
        cleaned_text = clean_text(segment.get('text', ''), list(swear_set))
        
        if not cleaned_text.strip():
            continue
        
        ratings = detox_model.predict(cleaned_text)
        if any([
            ratings.get('toxicity', 0) > thresholds[0],
            ratings.get('severe_toxicity', 0) > thresholds[1],
            ratings.get('obscene', 0) > thresholds[2],
            ratings.get('threat', 0) > thresholds[5],
            ratings.get('insult', 0) > thresholds[4],
            ratings.get('identity_attack', 0) > thresholds[3],
        ]):
            segments_to_mute.append(SegmentToMute(
                float(segment['start']),
                float(segment['end'])
            ))
    
    return words_to_mute, segments_to_mute

def readfromFile(testfile):
    with open(testfile, "r") as file:
        return file.read()

def mute_words(input_file: str, output_file: str, words_to_mute: list, segments_to_mute: list) -> None:
    if not words_to_mute and not segments_to_mute:
        subprocess.run(['cp', input_file, output_file], check=False)
        return


    all_segments = [(float(w.start), float(w.end)) for w in words_to_mute]
    all_segments.extend([(float(s.start), float(s.end)) for s in segments_to_mute])
    
    if not all_segments:
        subprocess.run(['cp', input_file, output_file], check=False)
        return


    all_segments.sort()
    merged = []
    for start, end in all_segments:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    print(f"Merged segments to remove: {merged}")

    duration = get_audio_duration(input_file)
    if duration is None:
        return

    segments_to_keep = []
    current_pos = 0.0
    
    for start, end in merged:
        if current_pos < start:
            segments_to_keep.append((current_pos, start))
        current_pos = max(current_pos, end)
    
    if current_pos < duration:
        segments_to_keep.append((current_pos, duration))

    if not segments_to_keep:
        print("All audio removed, creating silent file")
        subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', '0.1', output_file], capture_output=True)
        return


    with tempfile.TemporaryDirectory() as temp_dir:
        file_ext = Path(input_file).suffix
        segment_files = []
        
        try:
            for i, (start, end) in enumerate(segments_to_keep):
                segment_file = os.path.join(temp_dir, f"segment_{i}{file_ext}")
                segment_files.append(segment_file)
                duration_segment = end - start
                
                cmd = ['ffmpeg', '-y', '-i', input_file, '-ss', str(start), '-t', str(duration_segment), '-vn', '-c:a', 'copy', segment_file]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Failed to extract segment {i}:\n{result.stderr}")
                    return

            if len(segment_files) == 1:
                subprocess.run(['cp', segment_files[0], output_file], check=False)
            else:
                concat_file = os.path.join(temp_dir, "concat.txt")
                with open(concat_file, 'w') as f:
                    f.write('\n'.join(f"file '{seg}'" for seg in segment_files))
                
                cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file, '-c:a', 'copy', '-map_metadata', '0', output_file]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Concatenation failed:\n{result.stderr}")
                    return

            print(f"Output written to {output_file}")
        except Exception as e:
            print(f"Error processing audio: {e}")

def run_program(config_dict: dict) -> list | None:
    model_size = config_dict["model_size"]
    path = config_dict["file_path"]
    worker_counts = int(config_dict["worker_count"])
    
    thresholds = [
        config_dict["t"],
        config_dict["st"],
        config_dict["o"],
        config_dict["id"],
        config_dict["i"],
        config_dict["th"]
    ]
    
    bad_words = read_json("swears.json") or {"swears": []}
    
    global detox_model
    detox_model = Detoxify('original')

    input_path = os.path.join(path, 'Input')
    output_path = os.path.join(path, 'Output')

    in_files = {f for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f)) and not f.startswith('.')}
    out_files = {f for f in os.listdir(output_path) if os.path.isfile(os.path.join(output_path, f)) and not f.startswith('.')}
    
    working_list = sorted(in_files - out_files)
    
    if not working_list:
        print("No files to update")
        return None

    global global_pool
    results = []
    
    try:
        with multiprocessing.Pool(processes=worker_counts, initializer=worker_initializer, initargs=(model_size,)) as pool:
            global_pool = pool

            job_to_filename = {}
            for filename in working_list:
                async_result = pool.apply_async(process_file, (filename, input_path))
                job_to_filename[async_result] = filename

            pending = list(job_to_filename.keys())
            while pending:
                for async_result in list(pending):
                    if async_result.ready():
                        filename = job_to_filename[async_result]
                        transcribed_file = async_result.get()
                        results.append(transcribed_file)
                        words_to_mute, segments_to_mute = audio_cleaner(transcribed_file, bad_words, thresholds)
                        mute_words(
                            os.path.join(input_path, filename),
                            os.path.join(output_path, filename),
                            words_to_mute,
                            segments_to_mute
                        )
                        pending.remove(async_result)
            
            global_pool = None
            return results
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected, shutting down...")
        if global_pool:
            global_pool.terminate()
            global_pool.join()
        raise
    except Exception as e:
        print(f"Error during processing: {e}")
        if global_pool:
            global_pool.terminate()
            global_pool.join()
        raise