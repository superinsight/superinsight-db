from storage.model import StorageModel
from common.helper import CommonHelper
from environment import Environment
from common.source_location import SourceLocation
import torch
from common.logger import CommonLogger
import subprocess
import os, tempfile, json
import whisper
from pyannote.audio import Pipeline


class SpeechRecognitionPipeline:

    logger = None
    model_path = None
    device = None
    model = None
    speaker_verification_model = None
    storage_model = StorageModel()
    logger = CommonLogger()

    def __init__(self, logger=None, handler=None, model_path=None, use_gpu=False):
        self.logger = CommonLogger(logger=logger, handler=handler)
        if model_path is not None:
            self.model_path = model_path
        self.logger.info(
            "SpeechRecognitionPipeline init model_path:{}".format(str(self.model_path))
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = whisper.load_model(self.model_path)
        self.speaker_verification_model = Pipeline.from_pretrained(
            Environment.speaker_diarization_model,
            use_auth_token=Environment.hf_use_auth_token,
        )

    def __del__(self):
        self.logger.info(
            "SpeechRecognitionPipeline existing model_path:{}".format(
                str(self.model_path)
            )
        )

    def exec(self, inputs):
        common_helper = CommonHelper()
        source_location = common_helper.get_source_location(inputs)
        source_file = None
        if source_location == SourceLocation.URL:
            source_file = common_helper.localize_file_from_url(target=inputs)
        if source_location == SourceLocation.FILE_SYSTEM:
            source_file = common_helper.localize_file_from_file_system(target=inputs)
        if source_location == SourceLocation.S3:
            source_file = common_helper.localize_file_from_s3(target=inputs)
        if source_file is None:
            return None
        conversation = self._transcribe(source_file=source_file)
        return conversation

    def _trim_audio(self, source, start, end, destination):
        command = [
            "ffmpeg",
            "-i",
            str(source),
            "-ss",
            str(start),
            "-to",
            str(end),
            "-c",
            "copy",
            str(destination),
        ]
        self.logger.info("SpeechRecognitionPipeline._trim_audio:command", command)
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result

    def _convert_to_wave(self, source):
        base_name = os.path.basename(source)
        file_name, file_extension = base_name.split(".")
        if file_extension.lower() == "wav":
            return source
        temp_dir = tempfile.mkdtemp()
        destination = "{}/{}.wav".format(temp_dir, file_name)
        command = ["ffmpeg", "-i", str(source), str(destination)]
        self.logger.info("SpeechRecognitionPipeline._trim_audio:command", command)
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return destination

    def _convert_to_conversation(self, source):
        diarization = self.speaker_verification_model(source)
        conversation = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            part = {}
            part["start"] = turn.start
            part["end"] = turn.end
            part["speaker"] = speaker
            conversation.append(part)
        return conversation

    def _convert_to_transcript(self, source):
        return self.model.transcribe(source)

    def _transcribe(self, source_file):
        source_file = self._convert_to_wave(source_file)
        conversation = self._convert_to_conversation(source_file)
        self.logger.info(
            "SpeechRecognitionPipeline._transcribe:conversation",
            json.dumps(conversation),
        )
        temp_dir = tempfile.mkdtemp()
        index = 0
        for part in conversation:
            try:
                part_file = "{}/{}.wav".format(temp_dir, index)
                self._trim_audio(
                    source=source_file,
                    start=part["start"],
                    end=part["end"],
                    destination=part_file,
                )
                index = index + 1
                transcript = self._convert_to_transcript(part_file)
                part["transcript"] = transcript["text"]
                part["language"] = transcript["language"]
            except Exception as e:
                self.logger.error(e)
        return conversation
