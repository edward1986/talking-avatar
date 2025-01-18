import subprocess
import os
import uuid
import pyttsx3
from pathlib import Path

def generate_content(prompt):
    result = subprocess.run(
        ["ollama", "run", "llama3", prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Error generating content: {result.stderr.strip()}")
    return result.stdout.strip()

def check_files_exist():
    required_files = [
        "Wav2Lip/checkpoints/wav2lip_gan.pth",
        "Wav2Lip/checkpoints/mobilenet.pth",
        "host_a_avatar.png",
        "host_b_avatar.png",
        "guest_avatar.png",
    ]
    for file in required_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Required file not found: {file}")
    print("All required files are available.")

def text_to_speech(text, filename):
    engine = pyttsx3.init()
    engine.save_to_file(text, filename)
    engine.runAndWait()
    print(f"Saved audio to {filename}")
    duration = get_media_duration(filename)
    print(f"Audio duration: {duration} seconds")

def create_talking_head(audio_file, image_file):
    video_output = f"{Path(audio_file).stem}_video.mp4"
    command = (
        f"python Wav2Lip/inference.py --checkpoint_path Wav2Lip/checkpoints/wav2lip_gan.pth "
        f"--face {image_file} --audio {audio_file} --outfile {video_output}"
    )
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Generated video: {video_output}")
        duration = get_media_duration(video_output)
        print(f"Video duration: {duration} seconds")
    except subprocess.CalledProcessError as e:
        print(f"Error generating video: {e.stderr}")
        raise
    return video_output

def combine_all_videos_to_one(output_file, video_files):
    list_file = "video_list.txt"
    with open(list_file, "w") as f:
        for video in video_files:
            f.write(f"file '{video}'\n")
    
    command = f"ffmpeg -f concat -safe 0 -i {list_file} -c copy {output_file}"
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Final combined video saved as: {output_file}")
        duration = get_media_duration(output_file)
        print(f"Final video duration: {duration} seconds")
    except subprocess.CalledProcessError as e:
        print(f"Error combining videos: {e.stderr}")
        raise
    finally:
        os.remove(list_file)

def get_media_duration(file_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-i", file_path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting duration for {file_path}: {e}")
        return 0.0

def podcast_simulation():
    check_files_exist()

    roles = ["host_a", "host_b", "guest"]
    all_videos = []

    for turn in range(3):
        video_files = {}

        for role in roles:
            prompt = f"Role: {role}, Turn: {turn}, Provide a detailed discussion on AI advancements."
            response = generate_content(prompt)
            print(f"{role.capitalize()} response: {response}")

            audio_file = f"{role}_{turn}.mp3"
            text_to_speech(response, audio_file)

            video_file = create_talking_head(audio_file, f"{role}_avatar.png")
            video_files[role] = video_file

        all_videos.extend(video_files.values())

    final_output_file = f"{uuid.uuid4()}_final_output.mp4"
    combine_all_videos_to_one(final_output_file, all_videos)

if __name__ == "__main__":
    podcast_simulation()
