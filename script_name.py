import subprocess
import os
import pyttsx3
from transformers import AutoModelForCausalLM, AutoTokenizer
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# Load AI models and tokenizers
def load_model_and_tokenizer(model_name):
    """Load a Hugging Face model and tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Set the pad_token if not already set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    return model, tokenizer

# Initialize models for each role
host_a_model, host_a_tokenizer = load_model_and_tokenizer("EleutherAI/gpt-neo-1.3B")
host_b_model, host_b_tokenizer = load_model_and_tokenizer("EleutherAI/gpt-neo-1.3B")
guest_ai_model, guest_ai_tokenizer = load_model_and_tokenizer("EleutherAI/gpt-neo-1.3B")

# Role definitions
roles = {
    "host_a": "You are a curious podcast host. Your goal is to ask thought-provoking questions.",
    "host_b": "You are the co-host. Your goal is to challenge ideas humorously and add commentary.",
    "guest_ai": "You are a technology expert. Provide detailed and engaging answers on any topic."
}

def generate_response(model, tokenizer, prompt):
    """Generate a response using the Hugging Face model."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512, padding=True)
    outputs = model.generate(
        inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=50,  # Generate up to 50 new tokens
        num_return_sequences=1,
        do_sample=True,
        pad_token_id=tokenizer.pad_token_id,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
def send_message(agent, context, role_prompt):
    """Generate a response locally using Hugging Face models."""
    full_prompt = f"{role_prompt}\nUser: {context}\nAI:"
    if agent == "host_a":
        return generate_response(host_a_model, host_a_tokenizer, full_prompt)
    elif agent == "host_b":
        return generate_response(host_b_model, host_b_tokenizer, full_prompt)
    elif agent == "guest_ai":
        return generate_response(guest_ai_model, guest_ai_tokenizer, full_prompt)

# Convert text to speech using pyttsx3
def text_to_speech(text, filename):
    """Convert text to speech and save as an MP3 file offline."""
    engine = pyttsx3.init()
    engine.save_to_file(text, filename)
    engine.runAndWait()
    print(f"Saved audio to {filename}")

# Create a talking head video using Wav2Lip
def create_talking_head_wav2lip(audio_file, image_file):
    """Generate a talking head video using Wav2Lip."""
    video_output = "output_talking_head.mp4"
    command = (
        f"python Wav2Lip/inference.py --checkpoint_path Wav2Lip/checkpoints/wav2lip_gan.pth "
        f"--face {image_file} --audio {audio_file} --outfile {video_output}"
    )
    subprocess.run(command, shell=True)
    print(f"Generated video: {video_output}")
    return video_output

# Combine audio and video using FFmpeg
def combine_audio_video(video_file, audio_file, output_file):
    """Combine video and audio into a single file."""
    command = f"ffmpeg -i {video_file} -i {audio_file} -c:v copy -c:a aac {output_file}"
    subprocess.run(command, shell=True)
    print(f"Output saved to {output_file}")

# Podcast simulation with visuals and speech
def podcast_simulation_with_visuals():
    context = "Welcome to our podcast! Today, we'll discuss the future of artificial intelligence."
    turn_limit = 3  # Limit turns for demo
    turn = 0

    while turn < turn_limit:
        # Host A generates response
        response_a = send_message("host_a", context, roles["host_a"])
        print(f"Host A: {response_a}")
        text_to_speech(response_a, f"response_a_{turn}.mp3")
        video_a = create_talking_head_wav2lip(f"response_a_{turn}.mp3", "host_a_avatar.png")

        # Host B responds
        response_b = send_message("host_b", response_a, roles["host_b"])
        print(f"Host B: {response_b}")
        text_to_speech(response_b, f"response_b_{turn}.mp3")
        video_b = create_talking_head_wav2lip(f"response_b_{turn}.mp3", "host_b_avatar.png")

        # Guest AI adds commentary
        response_guest = send_message("guest_ai", response_b, roles["guest_ai"])
        print(f"Guest AI: {response_guest}")
        text_to_speech(response_guest, f"response_guest_{turn}.mp3")
        video_guest = create_talking_head_wav2lip(f"response_guest_{turn}.mp3", "guest_avatar.png")

        # Combine all outputs for this turn
        combine_audio_video(video_a, f"response_a_{turn}.mp3", f"final_host_a_{turn}.mp4")
        combine_audio_video(video_b, f"response_b_{turn}.mp3", f"final_host_b_{turn}.mp4")
        combine_audio_video(video_guest, f"response_guest_{turn}.mp3", f"final_guest_{turn}.mp4")

        context = response_guest
        turn += 1

    print("Podcast simulation complete with visuals and speech!")

podcast_simulation_with_visuals()
