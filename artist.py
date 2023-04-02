import torch
from PIL import Image
from io import BytesIO
import time
import datetime

from diffusers import DiffusionPipeline, StableDiffusionImg2ImgPipeline, StableDiffusionInpaintPipeline, DPMSolverMultistepScheduler

from flask import Flask, send_file, request, jsonify
from base64 import b64encode, b64decode


# ============= global settings =============
model_main = 'ogkalu/Comic-Diffusion'
model_inpaint = 'runwayml/stable-diffusion-inpainting'
dtype = torch.float16
img_size = (768, 768)
inference_steps = 50

# ============= load model =============
# UNFORTUNATELY, MY DESKTOP PC HAS ONLY 16GM RAM, SO ONLY ONE MODEL CAN BE LOADED AT A TIME
models = [
    DiffusionPipeline.from_pretrained(model_main, torch_dtype=dtype),
    # StableDiffusionImg2ImgPipeline.from_pretrained(model_main, torch_dtype=dtype), 
    # StableDiffusionInpaintPipeline.from_pretrained(model_inpaint, torch_dtype=dtype),
]
txt2img = 0
img2img = 1
# inpaint = 2

# set scheduler
models[txt2img].scheduler = DPMSolverMultistepScheduler.from_config(models[txt2img].scheduler.config)
# inpaint.scheduler = DPMSolverMultistepScheduler.from_config(inpaint.scheduler.config)
inference_steps = 30

# ============= utils =============
def timename():
    t = time.time()
    t = datetime.datetime.fromtimestamp(t).strftime('%d_%H-%M-%S')
    return str(t)

def save_imgs(imgs, path, prefix=None):
    prefix = prefix or timename()
    for i, img in enumerate(imgs):
        img.save(f'{path}/{prefix}_{i}.png')

def model_to_gpu(model):
    # unload the rest
    for i, m in enumerate(models):
        if i != model:
            models[model] = models[model].to('cpu')

    models[model] = models[model].to('cuda')

def get_inputs(prompt, batch_size=1):                                                                                                                                                                                                                 
#   generator = [torch.Generator("cuda").manual_seed(i) for i in range(batch_size)]                                                                                                                                                             
    prompts = batch_size * [prompt]
#   num_inference_steps = 20                                                                                                                                                                                                                    
    return prompts

#   return {"prompt": prompts, "generator": generator, "num_inference_steps": num_inference_steps}  


# ============= inference =============

# txt2img
def generate_txt2img(prompt, steps=inference_steps, gen=None):
    model_to_gpu(txt2img)
    return models[txt2img](4 * [prompt], num_inference_steps=steps, generator=gen).images


# img2img
def generate_img2img(input_img, prompt, steps=inference_steps, gen=None):
    model_to_gpu(img2img)
    input_img = input_img.resize(img_size).convert("RGB")

    return models[img2img](prompt=prompt, image=input_img, strength=0.8, guidance_scale=7.5, num_inference_steps=steps, generator=gen).images

# inpaint
# def generate_inpaint(input_img, mask_img, prompt, steps=inference_steps, gen=None):
#     model_to_gpu(inpaint)
#     img = img.resize(img_size).convert("RGB")
#     mask = mask.resize(img_size).convert("RGB")

#     return models[inpaint](prompt=prompt, image=img, mask_image=mask, num_inference_steps=steps, generator=gen).images


# ============= server ============= 

def compress(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return img_io

def encode(img):
    return b64encode(img.read()).decode('utf-8')

def decode(img_b64):
    return Image.open(BytesIO(b64decode(img_b64)))

def serve(img):
    return send_file(img, mimetype='image/jpeg')

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "hello world, i'm a comic artist!"

@app.route("/draw", methods=['GET'])
def serve_draw():
    prompt = request.args.get('prompt')
    if request.args.get('steps'):
        steps = int(request.args.get('steps'))
    else:
        steps = inference_steps

    img = generate_txt2img(prompt, steps)[0]
    return serve(compress(img))

@app.route("/txt2img", methods=['POST'])
def serve_txt2img():
    js = request.get_json()
    prompt = js.get('prompt')
    if js.get('steps'):
        steps = int(js.get('steps'))
    else:
        steps = inference_steps

    imgs = generate_txt2img(prompt, steps)
    imgs = [encode(compress(img)) for img in imgs]
    return jsonify(imgs)

@app.route("/img2img", methods=['POST'])
def serve_img2img():
    js = request.get_json()
    prompt = js.get('prompt')
    input_img = decode(js.get('input_img'))
    if js.get('steps'):
        steps = int(js.get('steps'))
    else:
        steps = inference_steps

    imgs = generate_img2img(input_img, prompt, steps)
    imgs = [encode(compress(img)) for img in imgs]
    return jsonify(imgs)

