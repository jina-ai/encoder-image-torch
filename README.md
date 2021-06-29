# ✨ ImageTorchEncoder

**ImageTorchEncoder** wraps the models from [torchvision](https://pytorch.org/vision/stable/index.html).

**ImageTorchEncoder** encodes `Document` blobs of type a `ndarray` and shape Batch x Height x Width x Channel 
into a `ndarray` of Batch x Dim and stores them in the `embedding` attribute of the `Document`.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [🌱 Prerequisites](#-prerequisites)
- [🚀 Usages](#-usages)
- [🎉️ Example](#%EF%B8%8F-example)
- [🔍️ Reference](#%EF%B8%8F-reference)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## 🌱 Prerequisites

None

## 🚀 Usages

### 🚚 Via JinaHub (WIP)
Use the prebuilt images from JinaHub in your python codes.
With the `volumes` argument you can pass model from your local machine into the Docker container.
```python
from jina import Flow

flow = Flow().add(uses='jinahub+docker://ImageTorchEncoder',
		  volumes='/your_home_folder/.cache/torch:/root/.cache/torch')
```
Alternatively, reference the docker image in the `yml` config
```yaml
jtype: Flow
pods:
  - name: encoder
    uses: 'jinahub+docker://ImageTorchEncoder'
    volumes: '/your_home_folder/.cache/torch:/root/.cache/torch'
```

### 📦️ Via PyPi
1. Install the `ImageTorchEncoder` 
```bash
pip install git+https://github.com/jina-ai/executor-image-torch-encoder.git
```
2. Use the `ImageTorchEncoder` in your code
```python
from jinahub.image.encoder import ImageTorchEncoder
from jina import Flow

f = Flow().add(uses=ImageTorchEncoder)
```

### 🐳 Via Docker
1. Clone the repo and build the docker image
```bash
git clone https://github.com/jina-ai/executor-text-paddle.git
cd executor-image-torch-encoder 
docker build -t jinahub-image-torch-encoder .
```
2. Use `jinahub-image-torch-encoder` in your codes
````python
from jina import Flow

f = Flow().add(
        uses='docker://jinahub-image-torch-encoder:latest',
        volumes='/your_home_folder/.cache/torch:/root/.cache/torch')
````

1. Use `executor-image-torch-encoder` in your codes
```python
from jina import Flow
f = Flow().add(uses='docker://executor-image-torch-encoder:latest')
```
	

## 🎉️ Example 

```python
import numpy as np

from jina import Flow, Document

f = Flow().add(
    uses='jinahub+docker://ImageTorchEncoder')

doc = Document(blob=np.ones((224, 224, 3), dtype=np.uint8))

with f:
    resp = f.post(on='/index', inputs=doc, return_results=True)
    print(f'{resp}')
```

### Inputs 
`Document` with `blob` of the shape `H x W x C`. 
Note that the `ImageTorchEncoder` by default resize and normalizes the image before inference.
Preprocessing can be disabled by setting `use_default_preprocessing=False` in the constructor.

### Returns
`Document` with `embedding` fields filled with an `ndarray` of the shape `embedding_dim` (size depends on the model) with `dtype=float32`.

## 🔍️ Reference
- [PyTorch TorchVision Transformers Preprocessing](https://sparrow.dev/torchvision-transforms/)