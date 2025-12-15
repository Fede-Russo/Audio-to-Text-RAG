from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch

class Transcriber:
    def __init__(self, config):
        
        self.model_id = config.TRANSCRIBER_MODEL
        self.lang = config.FORCED_LANGUAGE
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id, dtype=self.torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )

        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(self.model_id)

        self.pipeline = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            return_timestamps=True,
            feature_extractor=self.processor.feature_extractor,
            batch_size = 4,
            dtype=self.torch_dtype,
            device=self.device,
            generate_kwargs={"language": self.lang}
        )

    def transcribe(self, audio_path):
        result = self.pipeline(audio_path)
        return result