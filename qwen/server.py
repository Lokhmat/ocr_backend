from fastapi import FastAPI, UploadFile
from transformers import AutoProcessor, AutoModelForVision2Seq
import torch
from PIL import Image
import io

app = FastAPI()

processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")
model = AutoModelForVision2Seq.from_pretrained("Qwen/Qwen2-VL-2B-Instruct").to("cuda" if torch.cuda.is_available() else "cpu")

@app.post("/generate")
async def generate(file: UploadFile, prompt: str):
    image = Image.open(io.BytesIO(await file.read())).convert("RGB")
    inputs = processor(prompt=prompt, images=image, return_tensors="pt").to(model.device)
    generated_ids = model.generate(**inputs)
    result = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return {"response": result}
