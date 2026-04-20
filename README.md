# Visual Product Matcher (Zero-Shot Image-to-Image Search)

An independent, completely self-hosted **Visual Search Engine** built with a messaging interface, powered by **OpenAI's CLIP model**. This project demonstrates how to build a high-performance image matching pipeline from scratch without relying on expensive, cloud-hosted enterprise APIs like Google Vision.

## 🚀 Features
- **Zero-Shot Image-to-Image Matching**: Upload any image. The system computes 512-dimensional vector embeddings and calculates exact Cosine Similarities against the local inventory database instantly. No data-labeling or fine-tuning required.
- **Multi-Reference Robustness**: Overcome AI composition bias natively. Add multiple angles of an item (e.g., `Nike Shirt Front.png` and `Nike Shirt Back.png`), and the API will automatically vector them independently but map them back to the same root inventory count!
- **Pure Python Microservice**: The heavy AI logic is decoupled into a blazing-fast **FastAPI** backend. It loads the PyTorch CLIP model exactly once directly into memory array for zero-latency image processing.
- **100% Privacy & Independence**: Avoid pay-per-request API traps. All inferences run entirely locally on your own hardware using open-source PyTorch models.

---

## 🛠️ Tech Stack
- **AI / ML Core**: PyTorch, OpenAI CLIP (`ViT-B/32`)
- **Backend API**: Python, FastAPI, Uvicorn 
- **Frontend**: React, Vite, Axios, pure CSS (Glassmorphism)

---

## ⚙️ How to Run Locally

Because of the microservice architecture, you must run the Python Backend and the React Frontend simultaneously in two separate terminals.

### 1. Start the AI Microservice (Backend)
Open your first terminal and navigate to the backend folder:
```bash
cd backend

# Create a fresh virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate
# Activate it (Mac/Linux)
# source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Boot up the FastAPI server
python main.py
```
*Wait until you see `Uvicorn running on http://127.0.0.1:8000`*

### 2. Start the User Interface (Frontend)
Open your second terminal and navigate to the frontend folder:
```bash
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```
Click the local link (usually `http://localhost:5173`) to launch the UI in your browser!

---

## 📝 How to Test the Vision System
1. Go to the `backend/inventory_images/` folder.
2. Drop in any `.jpg` or `.png` images of your products. The file name will act as the object's label. 
3. **Pro-Tip**: You can add multiple angles of the same product for incredible accuracy! Just add suffixes like `Jordan Sport Front.png` and `Jordan Sport Back.png`. The backend inherently maps them back to the `"jordan sport"` stock quantities in `inventory.json`.
4. Restart the Python server (`Ctrl+C` then `python main.py`). It will automatically convert everything inside that folder into vector datasets in RAM.
5. Go to the React frontend, click the `💬 Support` button, and upload a test image to see the math in action!
