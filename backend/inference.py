import gc

import numpy as np
import torch

from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

models = {
  'vit_b': './checkpoints/sam_vit_b_01ec64.pth',
  'vit_l': './checkpoints/sam_vit_l_0b3195.pth',
  'vit_h': './checkpoints/sam_vit_h_4b8939.pth'
}

def get_sam_predictor(device=None, image=None):
  sam2_checkpoint = "../checkpoints/sam2.1_hiera_large.pt"
  model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"
  sam2_model = build_sam2(model_cfg, sam2_checkpoint, device=device)

  predictor = SAM2ImagePredictor(sam2_model)
  if image is not None:
    predictor.set_image(image)
  return predictor

def run_inference(predictor, input_x, selected_points,
                  multi_object: bool = False):
  if len(selected_points) == 0:
    return []
  points = torch.Tensor(
      [p for p, _ in selected_points]
  ).to(predictor.device).unsqueeze(1)

  labels = torch.Tensor(
      [int(l) for _, l in selected_points]
  ).to(predictor.device).unsqueeze(1)

  # predict segmentation according to the boxes
  masks, scores, logits = predictor.predict(
    point_coords=points,
    point_labels=labels,
    multimask_output=True,
  )
  masks = torch.tensor(masks).unsqueeze(0)
  scores = torch.tensor(scores).unsqueeze(0)

  masks = masks[:, torch.argmax(scores, dim=1)]
  masks_pos = masks[labels[:, 0] == 1, 0].cpu().detach().numpy()
  masks_neg = masks[labels[:, 0] == 0, 0].cpu().detach().numpy()
  if not multi_object:
    if len(masks_neg) == 0:
      masks_neg = np.zeros_like(masks_pos)
    if len(masks_pos) == 0:
      masks_pos = np.zeros_like(masks_neg)
    masks_neg = masks_neg.max(axis=0, keepdims=True)
    masks_pos = masks_pos.max(axis=0, keepdims=True)
    masks = (masks_pos.astype(int) - masks_neg.astype(int)).clip(0, 1)
  else:
    masks = np.concatenate([masks_pos, masks_neg], axis=0)
  gc.collect()
  torch.cuda.empty_cache()

  return [(mask, f'mask_{i}') for i, mask in enumerate(masks)]
