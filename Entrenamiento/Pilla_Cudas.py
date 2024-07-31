import torch

device = "0" if torch.cuda.is_available() else "cpu"
print(f"{torch.cuda.is_available()} -> {device}")
print(torch.cuda.get_device_properties(0))
