import subprocess
import os
import pyttsx3
from transformers import AutoModelForCausalLM, AutoTokenizer

# Disable parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Constants for required files and settings
REQUIRED_FILES = [
    "Wav2Lip/checkpoints/wav2lip_gan.pth",
    "Wav2Lip/checkpoints/mobilenet.pth",
    "host_a_avatar.png",
    "host_b_avatar.png",
    "guest_avatar.png",
]

MODEL_NAME = "EleutherAI/gpt-neo-1.3B"
MAX_NEW_TOKENS = 50  # Limit for generated tokens
TURN_LIMIT = 3  # Number of conversation turns

# Check required files

def check_files_exist():
    for file in REQUIRED_FILES:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Required file not found: {file}")
    print("All required files are available.")

# Load model and tokenizer

def load_model_and_tokenizer(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer

# Generate response

def generate_response(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512, padding=True)
    outputs = model.generate(
        inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=MAX_NEW_TOKENS,
        num_return_sequences=1,
        do_sample=True,
        pad_token_id=tokenizer.pad_token_id,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Text-to-speech conversion

def text_to_speech(text, filename):
    engine = pyttsx3.init()
    engine.save_to_file(text, filename)
    engine.runAndWait()
    print(f"Saved audio to {filename}")

# Create talking head video

def create_talking_head(audio_file, image_file):
    video_output = f"{os.path.splitext(audio_file)[0]}_video.mp4"
    command = (
        f"python Wav2Lip/inference.py --checkpoint_path Wav2Lip/checkpoints/wav2lip_gan.pth "
        f"--face {image_file} --audio {audio_file} --outfile {video_output}"
    )
    subprocess.run(command, shell=True, check=True)
    print(f"Generated video: {video_output}")
    return video_output

# Combine audio and video

def combine_audio_video(video_file, audio_file, output_file):
    command = f"ffmpeg -i {video_file} -i {audio_file} -c:v copy -c:a aac {output_file}"
    subprocess.run(command, shell=True, check=True)
    print(f"Output saved to {output_file}")

# Main simulation function

def podcast_simulation():
    check_files_exist()

    # Load models for each role
    host_a_model, host_a_tokenizer = load_model_and_tokenizer(MODEL_NAME)
    host_b_model, host_b_tokenizer = load_model_and_tokenizer(MODEL_NAME)
    guest_model, guest_tokenizer = load_model_and_tokenizer(MODEL_NAME)

    roles = {
        "host_a": "You are a curious podcast host. Your goal is to ask thought-provoking questions.",
        "host_b": "You are the co-host. Your goal is to challenge ideas humorously and add commentary.",
        "guest_ai": "You are a technology expert. Provide detailed and engaging answers on any topic.",
    }

    context = "Welcome to our podcast! Today, we'll discuss the future of artificial intelligence."
    
    for turn in range(TURN_LIMIT):
        # Host A generates response
        response_a = generate_response(host_a_model, host_a_tokenizer, f"{roles['host_a']}\nUser: {context}\nAI:")
        print(f"Host A: {response_a}")
        audio_a = f"response_a_{turn}.mp3"
        text_to_speech(response_a, audio_a)
        video_a = create_talking_head(audio_a, "host_a_avatar.png")

        # Host B responds
        response_b = generate_response(host_b_model, host_b_tokenizer, f"{roles['host_b']}\nUser: {response_a}\nAI:")
        print(f"Host B: {response_b}")
        audio_b = f"response_b_{turn}.mp3"
        text_to_speech(response_b, audio_b)
        video_b = create_talking_head(audio_b, "host_b_avatar.png")

        # Guest AI adds commentary
        response_guest = generate_response(guest_model, guest_tokenizer, f"{roles['guest_ai']}\nUser: {response_b}\nAI:")
        print(f"Guest AI: {response_guest}")
        audio_guest = f"response_guest_{turn}.mp3"
        text_to_speech(response_guest, audio_guest)
        video_guest = create_talking_head(audio_guest, "guest_avatar.png")

        # Combine outputs for this turn
        combine_audio_video(video_a, audio_a, f"final_host_a_{turn}.mp4")
        combine_audio_video(video_b, audio_b, f"final_host_b_{turn}.mp4")
        combine_audio_video(video_guest, audio_guest, f"final_guest_{turn}.mp4")

        # Update context for next turn
        context = response_guest

    print("Podcast simulation complete with visuals and speech!")

if __name__ == "__main__":
    podcast_simulation()
