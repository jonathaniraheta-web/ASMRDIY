import os
from flask import Flask, render_template, request, send_file, jsonify
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import io

app = Flask(__name__)

_api_key = os.environ.get("ELEVENLABS_API_KEY")
if not _api_key:
    raise RuntimeError(
        "ELEVENLABS_API_KEY environment variable is not set. "
        "Please add it to your Replit Secrets before running the app."
    )
client = ElevenLabs(api_key=_api_key)

# ASMR-friendly voice settings: slow, soft, calm
ASMR_VOICE_SETTINGS = VoiceSettings(
    stability=0.85,
    similarity_boost=0.75,
    style=0.2,
    use_speaker_boost=False,
)

ASMR_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel — calm, soft voice


def build_asmr_script(project_title: str, steps: list[str]) -> str:
    """Wrap DIY steps in a calming ASMR-style narration script."""
    intro = (
        f"Welcome... Take a deep breath... and relax. "
        f"Today, we are going to work on a wonderful DIY project together: {project_title}. "
        f"There's no rush. We'll go through each step slowly and mindfully."
    )
    step_text = ""
    for i, step in enumerate(steps, start=1):
        step_text += f"Step {i}... {step}... Take your time. "
    outro = (
        "And that's it... You've done a wonderful job. "
        "Take a moment to appreciate what you've created. Well done."
    )
    return f"{intro}\n\n{step_text}\n\n{outro}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    project_title = data.get("title", "").strip()
    raw_steps = data.get("steps", "").strip()

    if not project_title or not raw_steps:
        return jsonify({"error": "Please provide a project title and steps."}), 400

    steps = [s.strip() for s in raw_steps.split("\n") if s.strip()]
    if not steps:
        return jsonify({"error": "Please provide at least one step."}), 400

    script = build_asmr_script(project_title, steps)

    try:
        audio_stream = client.text_to_speech.convert(
            voice_id=ASMR_VOICE_ID,
            text=script,
            model_id="eleven_multilingual_v2",
            voice_settings=ASMR_VOICE_SETTINGS,
        )
        audio_bytes = b"".join(audio_stream)
    except Exception as exc:
        return jsonify({"error": f"Audio generation failed: {exc}"}), 502

    return send_file(
        io.BytesIO(audio_bytes),
        mimetype="audio/mpeg",
        as_attachment=False,
        download_name="asmr_diy.mp3",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
