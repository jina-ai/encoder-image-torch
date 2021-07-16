__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from typing import Tuple, Dict, List

import pytest

import torch
import numpy as np
from jina import DocumentArray, Document


try:
    from torch_encoder import ImageTorchEncoder
except:
    from jinahub.image.encoder import ImageTorchEncoder


@pytest.mark.parametrize(
    ['content', 'out_shape'],
    [
        ([np.ones((10, 10, 3), dtype=np.uint8), (3, 224, 224)]),
        ([np.ones((360, 420, 3), dtype=np.uint8), (3, 224, 224)]),
        ([np.ones((300, 300, 3), dtype=np.uint8), (3, 224, 224)])
    ]
)
def test_preprocessing_reshape_correct(
        content: np.ndarray,
        out_shape: Tuple
):
    encoder = ImageTorchEncoder()

    reshaped_content = encoder._preprocess(content)

    assert reshaped_content.shape == out_shape, f'Expected shape {out_shape} but got {reshaped_content.shape}'


@pytest.mark.parametrize(
    'feature_map',
    [
        np.ones((1, 10, 10, 3)),
        np.random.rand(1, 224, 224, 3),
        np.zeros((1, 100, 100, 3))
    ]
)
def test_get_pooling(
    feature_map: np.ndarray,
):
    encoder = ImageTorchEncoder()

    feature_map_after_pooling = encoder._get_pooling(torch.from_numpy(feature_map))

    np.testing.assert_array_almost_equal(feature_map_after_pooling, np.mean(feature_map, axis=(2, 3)))


@pytest.mark.skipif(not torch.cuda.is_available(),
                    reason='requires GPU and CUDA')
def test_get_features_gpu():
    encoder = ImageTorchEncoder()
    arr_in = np.ones((2, 3, 10, 10), dtype=np.float32)

    encodings = encoder._get_features(torch.from_numpy(arr_in).to(encoder.device)).detach().cpu().numpy()

    assert encodings.shape == (2, 1280, 1, 1)


def test_get_features_cpu():
    encoder = ImageTorchEncoder(device='cpu')
    arr_in = np.ones((2, 3, 10, 10), dtype=np.float32)

    encodings = encoder._get_features(torch.from_numpy(arr_in)).detach().numpy()

    assert encodings.shape == (2, 1280, 1, 1)


@pytest.mark.parametrize(
    'traversal_paths, docs',
    [
        (('r', ), pytest.lazy_fixture('docs_with_blobs')),
        (('c', ), pytest.lazy_fixture('docs_with_chunk_blobs'))
    ]
)
def test_encode_image_returns_correct_length(traversal_paths: List[str], docs: DocumentArray) -> None:
    encoder = ImageTorchEncoder(default_traversal_paths=traversal_paths)

    encoder.encode(docs=docs, parameters={})

    for doc in docs.traverse_flat(traversal_paths):
        assert doc.embedding is not None
        assert doc.embedding.shape == (1280, )


@pytest.mark.parametrize(
    'model_name',
    [
        'densenet169',
        'mobilenet_v3_large',
    ]
)
def test_encodes_semantic_meaning(test_images: Dict[str, np.array], model_name: str):
    encoder = ImageTorchEncoder(model_name=model_name)
    embeddings = {}

    for name, image_arr in test_images.items():
        docs = DocumentArray([Document(blob=image_arr)])
        encoder.encode(docs, parameters={})
        embeddings[name] = docs[0].embedding

    def dist(a, b):
        a_embedding = embeddings[a]
        b_embedding = embeddings[b]
        return np.linalg.norm(a_embedding - b_embedding)

    small_distance = dist('banana1', 'banana2')
    assert small_distance < dist('banana1', 'airplane')
    assert small_distance < dist('banana1', 'satellite')
    assert small_distance < dist('banana1', 'studio')
    assert small_distance < dist('banana2', 'airplane')
    assert small_distance < dist('banana2', 'satellite')
    assert small_distance < dist('banana2', 'studio')
    assert small_distance < dist('airplane', 'studio')
    assert small_distance < dist('airplane', 'satellite')
    assert small_distance < dist('studio', 'satellite')


def test_no_preprocessing():
    encoder = ImageTorchEncoder(use_default_preprocessing=False)
    arr_in = np.ones((224, 224, 3), dtype=np.float32)
    docs = DocumentArray([Document(blob=arr_in)])

    encoder.encode(docs=docs, parameters={})

    assert docs[0].embedding.shape == (1000, )