from diffusers import PNDMScheduler, DDIMScheduler, LMSDiscreteScheduler
import mediapy as media
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline

scheduler = PNDMScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear", skip_prk_steps=True)
model_id = "CompVis/stable-diffusion-v1-4"
device = "cuda"
remove_safety = False
pipe = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16, revision="fp16", use_auth_token=False)
if remove_safety:
  pipe.safety_checker = lambda images, clip_input: (images, False)
prompt = "apple watch with small screen"
num_images = 1

prompts = [ prompt ] * num_images
images = pipe(prompts, guidance_scale=7.5, num_inference_steps=50).images
    
media.show_images(images)
images[0].save("output.jpg")