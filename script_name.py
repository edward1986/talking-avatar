import subprocess
import os
import pyttsx3
def generate_content(prompt):
    """
    Generate content dynamically using a language model.
    Args:
        prompt (str): The input prompt for content generation.
    Returns:
        str: The generated response.
    """
    result = subprocess.run(
        ["ollama", "run", "llama3", prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Error generating content: {result.stderr.strip()}")
    return result.stdout.strip()

# Constants for required files
REQUIRED_FILES = [
    "Wav2Lip/checkpoints/wav2lip_gan.pth",
    "Wav2Lip/checkpoints/mobilenet.pth",
    "host_a_avatar.png",
    "host_b_avatar.png",
    "guest_avatar.png",
]

TURN_LIMIT = 3  # Number of conversation turns

def check_files_exist():
    """
    Ensure all required files are present before execution.
    """
    for file in REQUIRED_FILES:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Required file not found: {file}")
    print("All required files are available.")

def text_to_speech(text, filename):
    """
    Convert text to speech and save it as an audio file.
    Args:
        text (str): Text to convert.
        filename (str): Name of the output audio file.
    """
    engine = pyttsx3.init()
    engine.save_to_file(text, filename)
    engine.runAndWait()
    print(f"Saved audio to {filename}")

def create_talking_head(audio_file, image_file):
    """
    Create a talking head video using Wav2Lip.
    Args:
        audio_file (str): Path to the input audio file.
        image_file (str): Path to the input image file.
    Returns:
        str: Path to the output video file.
    """
    video_output = f"{os.path.splitext(audio_file)[0]}_video.mp4"
    command = (
        f"python Wav2Lip/inference.py --checkpoint_path Wav2Lip/checkpoints/wav2lip_gan.pth "
        f"--face {image_file} --audio {audio_file} --outfile {video_output}"
    )
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Generated video: {video_output}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating video:\n{e.stderr}")
        raise
    return video_output

def combine_all_videos_to_one(output_file, video_files):
    """
    Combine all video files into a single output video.
    Args:
        output_file (str): Name of the final combined video file.
        video_files (list): List of video file paths to combine.
    """
    list_file = "video_list.txt"
    with open(list_file, "w") as f:
        for video in video_files:
            f.write(f"file '{video}'\n")
    
    command = f"ffmpeg -f concat -safe 0 -i {list_file} -c copy {output_file}"
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Final combined video saved as: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error combining videos:\n{e.stderr}")
        raise
    finally:
        os.remove(list_file)

def podcast_simulation():
    """
    Simulate a podcast by dynamically generating responses and creating videos.
    """
    check_files_exist()

    roles = ["host_a", "host_b", "guest"]
    all_videos = []

    for turn in range(TURN_LIMIT):
        video_files = {}

        for role in roles:
            prompt = f"Role: {role}, Turn: {turn}, Topic: AI"
            response = generate_content(prompt)
            print(f"{role.capitalize()}: {response}")

            audio_file = f"response_{role}_{turn}.mp3"
            video_file = f"response_{role}_{turn}_video.mp4"

            text_to_speech(response, audio_file)
            video_file = create_talking_head(audio_file, f"{role}_avatar.png")

            video_files[role] = video_file

        # Add individual videos for this turn to the master list
        all_videos.extend(video_files.values())

    # Combine all videos into a final output video
    combine_all_videos_to_one("final_output.mp4", all_videos)

    print("Podcast simulation complete with visuals and speech!")

if __name__ == "__main__":
    podcast_simulation()
