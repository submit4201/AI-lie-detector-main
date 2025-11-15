# export (example for a simple HF model)
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased")
model.eval()
input_ids = torch.randint(0, 100, (1,16))
torch.onnx.export(model, (input_ids,), "model.onnx", opset_version=13,
                  input_names=["input_ids"], output_names=["logits"])

# run with onnxruntime-directml
import onnxruntime as ort
sess = ort.InferenceSession("model.onnx", providers=["DmlExecutionProvider"])
print(sess.get_providers())