import os
import sys
from fastapi import FastAPI
from typing import Optional
from typing import List
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from pipeline.image_to_text import ImageToTextPipeline
from pipeline.image_classification import ImageClassificationPipeline
from pipeline.question_answering import QuestionAnsweringPipeline
from pipeline.summarization import SummarizationPipeline
from pipeline.text_generation import TextGenerationPipeline
from pipeline.translation import TranslationPipeline
from pipeline.zero_shot_classification import ZeroShotClassificationPipeline
from pipeline.zero_shot_image_classification import ZeroShotImageClassificationPipeline

app = FastAPI(docs_url=None, redoc_url=None)
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
version = "1.0.0"

@app.on_event("startup")
async def startup_event():
    print("app startup")


@app.get("/")
async def HealthCheck():
    return {"version": version}


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Superinsight Inference API Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png"
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="Superinsight Inference API Documentation",
        redoc_js_url="/static/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.png"
    )


class InferenceOptions(BaseModel):
    use_gpu: bool = False
    wait_for_model: bool = True

class ImageClassificationRequest(BaseModel):
    inputs: str
    model: str = "google/vit-large-patch32-384"
    options: InferenceOptions

class ImageToTextRequest(BaseModel):
    inputs: str
    model: str = "nlpconnect/vit-gpt2-image-captioning"
    options: InferenceOptions

class QuestionAnsweringInput(BaseModel):
    question: str = "What is my name?"
    context: str = "My name is Clara and I live in Berkeley."

class QuestionAnsweringRequest(BaseModel):
    inputs: QuestionAnsweringInput
    model: str = "deepset/roberta-base-squad2"
    options: InferenceOptions

class SpeechRecongitionRequest(BaseModel):
    inputs: str = "https://mystorage/somefile.mp3"
    model: str ="openai/whisper-tiny"
    options: InferenceOptions
    
class SummarizationRequest(BaseModel):
    inputs: str = "New York (CNN)When Liana Barrientos was 23 years old, she got married in Westchester County, New York. A year later, she got married again in Westchester County, but to a different man and without divorcing her first husband. Only 18 days after that marriage, she got hitched yet again. Then, Barrientos declared \"I do\" five more times, sometimes only within two weeks of each other. In 2010, she married once more, this time in the Bronx. In an application for a marriage license, she stated it was her \"first and only\" marriage. Barrientos, now 39, is facing two criminal counts of \"offering a false instrument for filing in the first degree,\" referring to her false statements on the 2010 marriage license application, according to court documents. Prosecutors said the marriages were part of an immigration scam. On Friday, she pleaded not guilty at State Supreme Court in the Bronx, according to her attorney, Christopher Wright, who declined to comment further. After leaving court, Barrientos was arrested and charged with theft of service and criminal trespass for allegedly sneaking into the New York subway through an emergency exit, said Detective Annette Markowski, a police spokeswoman. In total, Barrientos has been married 10 times, with nine of her marriages occurring between 1999 and 2002. All occurred either in Westchester County, Long Island, New Jersey or the Bronx. She is believed to still be married to four men, and at one time, she was married to eight men at once, prosecutors say. Prosecutors said the immigration scam involved some of her husbands, who filed for permanent residence status shortly after the marriages. Any divorces happened only after such filings were approved. It was unclear whether any of the men will be prosecuted. The case was referred to the Bronx District Attorney\'s Office by Immigration and Customs Enforcement and the Department of Homeland Security\'s Investigation Division. Seven of the men are from so-called \"red-flagged\" countries, including Egypt, Turkey, Georgia, Pakistan and Mali. Her eighth husband, Rashid Rajput, was deported in 2006 to his native Pakistan after an investigation by the Joint Terrorism Task Force. If convicted, Barrientos faces up to four years in prison.  Her next court appearance is scheduled for May 18."
    model: str = "facebook/bart-large-cnn"
    max_length: int = 0
    min_length: int = 0
    options: InferenceOptions


class TextGenerationRequest(BaseModel):
    inputs: str = "The sky is blue and the grass is"
    model: str = "EleutherAI/gpt-neo-125M"
    max_length: int = 10
    min_length: int = 0
    options: InferenceOptions


class TranslationRequest(BaseModel):
    inputs: str = "The sky is blue and the grass is green"
    model: str = "Helsinki-NLP/opus-mt-en-fr"
    model_type: str = ""
    src_lang: str = "en"
    tgt_lang: str = "fr"
    options: InferenceOptions


class ZeroShotClassificationParameters(BaseModel):
    candidate_labels: List[str] = ["refund", "legal", "faq"]


class ZeroShotClassificationRequest(BaseModel):
    inputs: str = "Hi, I recently bought a device from your company but it is not working as advertised and I would like to get reimbursed!"
    model: str = "facebook/bart-large-mnli"
    parameters: ZeroShotClassificationParameters
    options: InferenceOptions

class ZeroShotImageClassificationRequest(BaseModel):
    inputs: str = "https://myimage.jpeg"
    model: str = "openai/clip-vit-large-patch14"
    parameters: ZeroShotClassificationParameters
    options: InferenceOptions

@app.post("/image-classification")
async def image_classification(req: ImageClassificationRequest):
    """
    * model (used by passing the following model repo on huggince face or cloud storage provider)
        * google/vit-large-patch32-384
        * gs://my-finetuned-model/
    * inputs (url to generate text)
    """
    try:
        pipeline = ImageClassificationPipeline(
            model_path=req.model, use_gpu=req.options.use_gpu)
        output = pipeline.exec(
            inputs=req.inputs)
        return output
    except:
        print(sys.exc_info()[0])
        return {"status": "error"}

@app.post("/image-to-text")
async def image_to_text(req: ImageToTextRequest):
    """
    * model (used by passing the following model repo on huggince face or cloud storage provider)
        * nlpconnect/vit-gpt2-image-captioning
        * gs://my-finetuned-model/
    * inputs (url to generate text)
    """
    try:
        pipeline = ImageToTextPipeline(
            model_path=req.model, use_gpu=req.options.use_gpu)
        output = pipeline.exec(
            inputs=req.inputs)
        return output
    except:
        print(sys.exc_info()[0])
        return {"status": "error"}

@app.post("/question-answering")
async def question_answering(req: QuestionAnsweringRequest):
    """
    * model (used by passing the following model repo on huggince face or cloud storage provider)
        * deepset/roberta-base-squad2
        * gs://my-finetuned-model/
    * inputs (context and question to ask)
    """
    try:
        pipeline = QuestionAnsweringPipeline(
            model_path=req.model, use_gpu=req.options.use_gpu)
        output = pipeline.exec(
            inputs=req.inputs)
        return output
    except:
        print(sys.exc_info()[0])
        return {"status": "error"}

@app.post("/speech-recognition")
async def speech_recognition(req: SpeechRecongitionRequest):
    """
    * model (used by passing the following model repo on huggince face or cloud storage provider)
        * openai/whisper-tiny
        * gs://my-finetuned-model/
    * inputs (url or location of audio file)
    """
    try:
        return {"status": "error", "message":"Not Implemented Yet"}
    except:
        print(sys.exc_info()[0])
        return {"status": "error"}

@app.post("/summarization")
async def summarization(req: SummarizationRequest):
    """
    * model (used by passing the following model repo on huggince face or cloud storage provider)
        * facebook/bart-large-cnn
        * gs://my-finetuned-model/
    * inputs (inputs for text to summarize)
    * max_length (max_length of summary)
    * min_length (min_length of summary)
    """
    try:
        pipeline = SummarizationPipeline(
            model_path=req.model, use_gpu=req.options.use_gpu)
        output = pipeline.exec(
            article=req.inputs, min_length=req.min_length, max_length=req.max_length)
        return output
    except:
        print(sys.exc_info()[0])
        return {"status": "error"}


@app.post("/text-generation")
async def text_generation(req: TextGenerationRequest):
    """
    * model (used by passing the following model repo on huggince face or cloud storage provider)
        * EleutherAI/gpt-neo-125M
        * gs://my-finetuned-model/
    * inputs (inputs for text as prompt)
    """
    try:
        pipeline = TextGenerationPipeline(
            model_path=req.model, use_gpu=req.options.use_gpu)
        output = pipeline.exec(
            prompt=req.inputs, min_length=req.max_length, max_length=req.max_length)
        return {"status": "success", "output": output}
    except:
        print(sys.exc_info())
        return {"status": "error"}


@app.post("/translation")
async def translation(req: TranslationRequest):
    """
    * model (used by passing the following model repo on huggince face or cloud storage provider)
        * facebook/mbart-large-50-many-to-many-mmt"
        * Helsinki-NLP/opus-mt-en-fr
        * gs://my-finetuned-model/
    * inputs (source to translate)
    * type (the type of model)
        * mbart
        * None
    * src_lang (source language)
        * en_XX
        * en
    * tgt_lang (target language)
        * fr_XX
        * fr
    """
    try:
        pipeline = TranslationPipeline(
            model_path=req.model, model_type=req.model_type, use_gpu=req.options.use_gpu)
        output = pipeline.exec(
            input=req.inputs, src_lang=req.src_lang, tgt_lang=req.tgt_lang)
        return output
    except:
        print(sys.exc_info())
        return {"status": "error"}


@app.post("/zero-shot-classification")
async def zero_shot_classification(req: ZeroShotClassificationRequest):
    """
    * model (used by passing the following model repo on huggince face or cloud storage provider)
        * facebook/bart-large-mnli
        * gs://my-finetuned-model/
    * inputs (text to classify)
    * parameters
        * candidate_labels (labels to classify)
    """
    try:
        pipeline = ZeroShotClassificationPipeline(
            model_path=req.model, use_gpu=req.options.use_gpu)
        output = pipeline.exec(
            inputs=req.inputs, labels=req.parameters.candidate_labels)
        return output
    except:
        print(sys.exc_info()[0])
        return {"status": "error"}

@app.post("/zero-shot-image-classification")
async def zero_shot_image_classification(req: ZeroShotImageClassificationRequest):
    """
    * model (used by passing the following model repo on huggince face or cloud storage provider)
        * openai/clip-vit-large-patch14
        * gs://my-finetuned-model/
    * inputs (image_url to classify)
    * parameters
        * candidate_labels (labels to classify)
    """
    try:
        pipeline = ZeroShotImageClassificationPipeline(
            model_path=req.model, use_gpu=req.options.use_gpu)
        output = pipeline.exec(
            url=req.inputs, labels=req.parameters.candidate_labels)
        return output
    except:
        print(sys.exc_info()[0])
        return {"status": "error"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Superinsight Inference API Documentation",
        version=version,
        description="API to inference base or finetuned transformer models",
        routes=app.routes
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
