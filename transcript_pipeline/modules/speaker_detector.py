from pyannote.audio import Pipeline
import torch

class SpeakerDetector:

    def __init__(self,config):
        self.model_id = config.DIARIZATION_MODEL
        self.hf_token = config.HF_TOKEN
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.pipeline = Pipeline.from_pretrained(self.model_id, use_auth_token=self.hf_token)
        self.pipeline.to(self.device)

    def detect_speakers(self, audio_path):
        diarization = self.pipeline(audio_path)
        return diarization