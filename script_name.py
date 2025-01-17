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
    "guest_ai": [
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

def podcast_simulation():
    check_files_exist()

    for turn in range(TURN_LIMIT):
        # Host A speaks
        response_a = STATIC_RESPONSES["host_a"][turn]
        print(f"Host A: {response_a}")
        audio_a = f"response_a_{turn}.mp3"
        text_to_speech(response_a, audio_a)
        video_a = create_talking_head(audio_a, "host_a_avatar.png")

        # Host B responds
        response_b = STATIC_RESPONSES["host_b"][turn]
        print(f"Host B: {response_b}")
        audio_b = f"response_b_{turn}.mp3"
        text_to_speech(response_b, audio_b)
        video_b = create_talking_head(audio_b, "host_b_avatar.png")

        # Guest AI adds commentary
        response_guest = STATIC_RESPONSES["guest_ai"][turn]
        print(f"Guest AI: {response_guest}")
        audio_guest = f"response_guest_{turn}.mp3"
        text_to_speech(response_guest, audio_guest)
        video_guest = create_talking_head(audio_guest, "guest_avatar.png")

        # Combine outputs for this turn
        combine_audio_video(video_a, audio_a, f"final_host_a_{turn}.mp4")
        combine_audio_video(video_b, audio_b, f"final_host_b_{turn}.mp4")
        combine_audio_video(video_guest, audio_guest, f"final_guest_{turn}.mp4")

    print("Podcast simulation complete with visuals and speech!")

if __name__ == "__main__":
    podcast_simulation()
