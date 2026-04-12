import os

import librosa
import torch
from optimum.bettertransformer import BetterTransformer
from transformers import Wav2Vec2Processor

from src.core.model import Wav2Vec2ForWav2Vec2ForCTCAndUttranceRegression

os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

MODEL_NAME = "seba3y/wav2vec-base-en-pronunciation-assesment"
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'


def load_model_components():
    processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
    model = Wav2Vec2ForWav2Vec2ForCTCAndUttranceRegression.from_pretrained(MODEL_NAME).to(DEVICE)
    model = BetterTransformer.transform(model)
    return processor, model


def load_audio(audio_path: str, processor):
    audio, _ = librosa.load(audio_path, sr=16000)
    input_values = processor(audio, sampling_rate=16000, return_tensors="pt").input_values

    return input_values.to(DEVICE)


@torch.inference_mode()
def assess_audio_file(audio_path: str, processor, model) -> dict:
    input_values = load_audio(audio_path, processor)
    inference_output = model(input_values)
    result_scores = dict(inference_output.logits)
    result_scores.pop('logits', None)

    response = {
        'pronunciation_accuracy': round(result_scores['accuracy'].cpu().item()),
        'content_scores': round(result_scores['content'].cpu().item()),
        'total_score': round(result_scores['total score'].cpu().item()),
        'fluency_score': round(result_scores['fluency'].cpu().item()),
    }


    return response
