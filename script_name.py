import subprocess
import os
import pyttsx3

# Constants for required files
REQUIRED_FILES = [
    "Wav2Lip/checkpoints/wav2lip_gan.pth",
    "Wav2Lip/checkpoints/mobilenet.pth",
    "host_a_avatar.png",
    "host_b_avatar.png",
    "guest_avatar.png",
]

TURN_LIMIT = 3  # Number of conversation turns

# Static responses for each role
STATIC_RESPONSES = {
    "host_a": [
        "Welcome to our podcast! Today, we'll discuss the future of artificial intelligence.",
        "Artificial intelligence is transforming industries rapidly. What are your thoughts, co-host?",
        "Thanks for sharing your insights, guest! Let's dive deeper into AI ethics and regulation.",
    ],
    "host_b": [
        "That's a great question! AI is everywhere, but is it making life better or worse?",
        "I think AI is impressive, but sometimes it feels like it's taking over. Guest, what do you think?",
        "Ethics is a tricky topic. Do we trust AI to make fair decisions, or do humans need to stay in control?",
    ],
    "guest": [
        "AI has immense potential to improve lives, but we must be cautious about biases and misuse.",
        "AI is a tool. It amplifies human abilities, but we need to be mindful of how we use it.",
        "Regulating AI is essential. We need clear guidelines to ensure it benefits everyone without causing harm.",
    ],
}

def check_files_exist():
    for file in REQUIRED_FILES:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Required file not found: {file}")
    print("All required files are available.")

def text_to_speech(text, filename):
    engine = pyttsx3.init()
    engine.save_to_file(text, filename)
    engine.runAndWait()
    print(f"Saved audio to {filename}")

def create_talking_head(audio_file, image_file):
    video_output = f"{os.path.splitext(audio_file)[0]}_video.mp4"
    command = (
        f"python Wav2Lip/inference.py --checkpoint_path Wav2Lip/checkpoints/wav2lip_gan.pth "
        f"--face {image_file} --audio {audio_file} --outfile {video_output}"
    )
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Generated video: {video_output}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating video:\nCommand: {e.cmd}\nReturn Code: {e.returncode}\nOutput: {e.stderr}")
        raise
    return video_output

def combine_audio_video(video_file, audio_file, output_file):
    command = f"ffmpeg -i {video_file} -i {audio_file} -c:v copy -c:a aac {output_file}"
    subprocess.run(command, shell=True, check=True)
    print(f"Output saved to {output_file}")
def combine_all_videos_to_one(output_file, video_files):
    """
    Combines all video files into a single output video.
    
    Args:
        output_file (str): The name of the final combined video file.
        video_files (list): List of video file paths to combine.
    """
    # Create a temporary file to list all video files
    list_file = "video_list.txt"
    with open(list_file, "w") as f:
        for video in video_files:
            f.write(f"file '{video}'\n")
    
    # Use FFmpeg to concatenate videos
    command = f"ffmpeg -f concat -safe 0 -i {list_file} -c copy {output_file}"
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Final combined video saved as: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error combining videos:\nCommand: {e.cmd}\nReturn Code: {e.returncode}\nOutput: {e.stderr}")
        raise
    finally:
        # Clean up the temporary list file
        os.remove(list_file)

def podcast_simulation():
    check_files_exist()

    roles = ["host_a", "host_b", "guest_ai"]
    static_responses = STATIC_RESPONSES
    all_videos = []

    for turn in range(TURN_LIMIT):
        video_files = {}
        audio_files = {}

        for role in roles:
            response = static_responses[role][turn]
            print(f"{role.capitalize()}: {response}")
            audio_file = f"response_{role}_{turn}.mp3"
            video_file = f"response_{role}_{turn}_video.mp4"

            text_to_speech(response, audio_file)
            video_file = create_talking_head(audio_file, f"{role}_avatar.png")

            video_files[role] = video_file
            audio_files[role] = audio_file

        # Add all individual videos for this turn to the master list
        all_videos.extend(video_files.values())

    # Combine all videos into a final output video
    combine_all_videos_to_one("final_output.mp4", all_videos)

    print("Podcast simulation complete with visuals and speech!")

if __name__ == "__main__":
    podcast_simulation()
