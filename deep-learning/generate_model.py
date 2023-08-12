from optimum.onnxruntime import ORTModelForFeatureExtraction, ORTOptimizer, ORTQuantizer
from optimum.onnxruntime.configuration import OptimizationConfig, AutoQuantizationConfig
import os

model_checkpoint = "moka-ai/m3e-base"
save_directory = "model/"

os.system(f"rm -rf {save_directory}")

# Load a model from transformers and export it to ONNX
model = ORTModelForFeatureExtraction.from_pretrained(model_checkpoint, export=True)

# Optimize the model
optimizer = ORTOptimizer.from_pretrained(model)
model = optimizer.optimize(OptimizationConfig(optimization_level=99), save_directory)
