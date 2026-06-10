import io
import modal

# --- Config ---
MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"
MODEL_DIR = "/models/qwen3-tts"

volume = modal.Volume.from_name("qwen3-tts-cache", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "qwen-tts",
        "soundfile",
        "huggingface_hub[hf_transfer]",
        "torch",
    )
    .env({
        "HF_HUB_ENABLE_HF_TRANSFER": "1",
        "HF_HOME": MODEL_DIR,
    })
)

app = modal.App("qwen3-tts", image=image)


# --- Download (run once: `modal run tts.py::download_model`) ---
@app.function(volumes={MODEL_DIR: volume}, timeout=600)
def download_model():
    import os
    from huggingface_hub import snapshot_download

    model_path = f"{MODEL_DIR}/hub/models--Qwen--Qwen3-TTS-12Hz-1.7B-CustomVoice"
    if os.path.exists(model_path):
        print("Already downloaded, skipping.")
        return

    snapshot_download(repo_id=MODEL_ID, local_dir=model_path)
    volume.commit()
    print("Download complete.")


# --- Inference ---
@app.cls(gpu="L4", volumes={MODEL_DIR: volume}, timeout=300, scaledown_window=2)
class QwenTTS:
    @modal.enter()
    def load_model(self):
        import torch
        from qwen_tts import Qwen3TTSModel

        self.model = Qwen3TTSModel.from_pretrained(
            MODEL_ID,
            device_map="cuda:0",
            dtype=torch.bfloat16,
        )

    def _generate(self, text: str, speaker: str = "Ryan", language: str = "English", instruct: str = "") -> bytes:
        import soundfile as sf

        wavs, sr = self.model.generate_custom_voice(
            text=text, language=language, speaker=speaker, instruct=instruct
        )
        buf = io.BytesIO()
        sf.write(buf, wavs[0], sr, format="WAV")
        return buf.getvalue()

    @modal.method()
    def generate(self, text: str, speaker: str = "Ryan", language: str = "English", instruct: str = "") -> bytes:
        return self._generate(text, speaker, language, instruct)

    @modal.fastapi_endpoint(method="POST")
    def api(self, item: dict) -> "fastapi.responses.Response":
        import fastapi

        audio = self._generate(
            text=item.get("text", "Hello."),
            speaker=item.get("speaker", "Ryan"),
            language=item.get("language", "English"),
            instruct=item.get("instruct", ""),
        )
        return fastapi.responses.Response(content=audio, media_type="audio/wav")


# --- Local test (`modal run tts.py`) ---
@app.local_entrypoint()
def main():
    audio = QwenTTS().generate.remote(
        text="What's up dude, this is an AI voice.",
        speaker="Ryan",
        language="English",
        instruct="Casual and relaxed.",
    )
    with open("output.wav", "wb") as f:
        f.write(audio)
    print("Saved to output.wav")
