import clip
import torch
import json
import os
from PIL import Image
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import io

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = None, None

inventory_embeddings_image = {}
inventory_embeddings_text = {}
text_labels = []
inventory_data = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def load_model():
    global model, preprocess, text_labels, inventory_embeddings_text, inventory_embeddings_image, inventory_data
    print("Loading CLIP model ViT-B/32...")
    model, preprocess = clip.load("ViT-B/32", device=device)
    
    # Image-to-Image setup
    image_dir = os.path.join(os.path.dirname(__file__), 'inventory_images')
    if os.path.exists(image_dir) and len(os.listdir(image_dir)) > 0:
        for filename in os.listdir(image_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                img_path = os.path.join(image_dir, filename)
                try:
                    img = preprocess(Image.open(img_path)).unsqueeze(0).to(device)
                    with torch.no_grad():
                        img_feature = model.encode_image(img)
                        img_feature /= img_feature.norm(dim=-1, keepdim=True)
                        label = os.path.splitext(filename)[0].lower().replace('_', ' ').replace('-', ' ')
                        inventory_embeddings_image[label] = img_feature
                except Exception as e:
                    print(f"Failed {filename}: {e}")
    
    # Load inventory.json
    inventory_path = os.path.join(os.path.dirname(__file__), 'inventory.json')
    if os.path.exists(inventory_path):
        with open(inventory_path, 'r') as f:
            inventory_data = json.load(f)
            text_labels = list(inventory_data.keys())
            if "an unknown miscellaneous object" not in text_labels:
                text_labels.append("an unknown miscellaneous object")
                
        text_inputs = clip.tokenize(["a photo of " + t for t in text_labels]).to(device)
        with torch.no_grad():
            text_features = model.encode_text(text_inputs)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            inventory_embeddings_text = text_features

def process_image(image_bytes: bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        user_img = preprocess(image).unsqueeze(0).to(device)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image format")

    with torch.no_grad():
        user_image_feature = model.encode_image(user_img)
        user_image_feature /= user_image_feature.norm(dim=-1, keepdim=True)
        
        predictions = []
        if inventory_embeddings_image:
            labels = list(inventory_embeddings_image.keys())
            features = torch.cat(list(inventory_embeddings_image.values()), dim=0)
            similarity = (user_image_feature @ features.T)
            num_results = min(3, len(labels))
            values, indices = similarity[0].topk(num_results)
            for i, idx in enumerate(indices):
                predictions.append({"label": labels[idx.item()], "score": values[i].item(), "match_type": "image"})
        else:
            similarity = (user_image_feature @ inventory_embeddings_text.T)
            num_results = min(3, len(text_labels))
            values, indices = similarity[0].topk(num_results)
            for i, idx in enumerate(indices):
                predictions.append({"label": text_labels[idx.item()], "score": values[i].item(), "match_type": "text"})
                
        return predictions

@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...)):
    image_bytes = await file.read()
    predictions = process_image(image_bytes)
    
    match_type = predictions[0].get('match_type', 'text')
    threshold = 0.83 if match_type == 'image' else 0.25
    strong_matches = [p for p in predictions if p['score'] >= threshold and p['label'] != "an unknown miscellaneous object"]
    
    return {
        "uploaded_image": file.filename,
        "similar_products": strong_matches
    }

@app.post("/api/chat")
async def api_chat(image: UploadFile = File(...)):
    image_bytes = await image.read()
    predictions = process_image(image_bytes)
    
    top_match = predictions[0]["label"]
    confidence = predictions[0]["score"]
    match_type = predictions[0]["match_type"]
    
    threshold = 0.83 if match_type == 'image' else 0.25

    if confidence < threshold or top_match == "an unknown miscellaneous object":
        return {"reply": "I'm not exactly sure what item that is, or it's an item we definitively do not carry in our inventory system.", "predictions": predictions}

    # Map variant labels (like 'nike fairway fresh back') back to root item
    matched_inventory_key = top_match
    for key in inventory_data.keys():
        if top_match.startswith(key.lower()):
            matched_inventory_key = key
            break

    stock_data = inventory_data.get(matched_inventory_key)
    if stock_data and stock_data.get("quantity", 0) > 0:
        return {"reply": f"Yes! We currently have {stock_data['quantity']} units of {matched_inventory_key} physically in stock.", "predictions": predictions}
    else:
        return {"reply": f"I'm sorry, we are completely sold out of {matched_inventory_key} at this exact moment.", "predictions": predictions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
