from onnxruntime import InferenceSession
from tokenizers import Tokenizer
import os, sys, asyncio
import numpy as np

modelPath = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd(), "model")
model = None
tokenizer = None
embeddingsLock = asyncio.Lock()

def syncGetEmbeddings(text):
    inputs = tokenizer.encode_batch([text])
    input_ids = inputs[0].ids
    token_type_ids = inputs[0].type_ids
    attention_mask = inputs[0].attention_mask
    embeddings = model.run(None, {"input_ids": [input_ids], "token_type_ids": [token_type_ids], "attention_mask": [attention_mask]})
    embeddings = np.linalg.norm(np.array(embeddings[0][0]).mean(axis=0))
    return embeddings

async def getEmbeddings(text):
    global embeddingsLock
    async with embeddingsLock:
        return await asyncio.get_event_loop().run_in_executor(None, syncGetEmbeddings, text)

def calculateSimilarity(embeddings1, embeddings2):
    return np.dot(embeddings1, embeddings2)/(embeddings1*embeddings2)

async def initalizeDeepLearning():
    global model, tokenizer
    model = InferenceSession(os.path.join(modelPath, "model.onnx"))
    tokenizer = Tokenizer.from_file(os.path.join(modelPath, "tokenizer.json"))