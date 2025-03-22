from snac import SNAC
import numpy as np
import torch
import asyncio
import threading
import queue

# Initialize SNAC model for audio processing
try:
    # Use CPU instead of CUDA for better compatibility
    device = "cpu"
    model = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").eval()
    model = model.to(device)
    model_loaded = True
    print("SNAC model loaded successfully on CPU")
except Exception as e:
    print(f"Error loading SNAC model: {e}")
    model_loaded = False

def convert_to_audio(multiframe, count):
    """
    Convert token frames to audio using SNAC.
    
    Args:
        multiframe: List of token IDs
        count: Current token count
        
    Returns:
        Audio data as bytes or None if conversion fails
    """
    if not model_loaded:
        print("SNAC model not loaded, cannot convert to audio")
        return None
        
    try:
        frames = []
        if len(multiframe) < 7:
            return None

        # Use CPU instead of CUDA
        device = "cpu"
        codes_0 = torch.tensor([], device=device, dtype=torch.int32)
        codes_1 = torch.tensor([], device=device, dtype=torch.int32)
        codes_2 = torch.tensor([], device=device, dtype=torch.int32)

        num_frames = len(multiframe) // 7
        frame = multiframe[:num_frames*7]

        for j in range(num_frames):
            i = 7*j
            if codes_0.shape[0] == 0:
                codes_0 = torch.tensor([frame[i]], device=device, dtype=torch.int32)
            else:
                codes_0 = torch.cat([codes_0, torch.tensor([frame[i]], device=device, dtype=torch.int32)])

            if codes_1.shape[0] == 0:
                codes_1 = torch.tensor([frame[i+1]], device=device, dtype=torch.int32)
                codes_1 = torch.cat([codes_1, torch.tensor([frame[i+4]], device=device, dtype=torch.int32)])
            else:
                codes_1 = torch.cat([codes_1, torch.tensor([frame[i+1]], device=device, dtype=torch.int32)])
                codes_1 = torch.cat([codes_1, torch.tensor([frame[i+4]], device=device, dtype=torch.int32)])

            if codes_2.shape[0] == 0:
                codes_2 = torch.tensor([frame[i+2]], device=device, dtype=torch.int32)
                codes_2 = torch.cat([codes_2, torch.tensor([frame[i+3]], device=device, dtype=torch.int32)])
                codes_2 = torch.cat([codes_2, torch.tensor([frame[i+5]], device=device, dtype=torch.int32)])
                codes_2 = torch.cat([codes_2, torch.tensor([frame[i+6]], device=device, dtype=torch.int32)])
            else:
                codes_2 = torch.cat([codes_2, torch.tensor([frame[i+2]], device=device, dtype=torch.int32)])
                codes_2 = torch.cat([codes_2, torch.tensor([frame[i+3]], device=device, dtype=torch.int32)])
                codes_2 = torch.cat([codes_2, torch.tensor([frame[i+5]], device=device, dtype=torch.int32)])
                codes_2 = torch.cat([codes_2, torch.tensor([frame[i+6]], device=device, dtype=torch.int32)])

        codes = [codes_0.unsqueeze(0), codes_1.unsqueeze(0), codes_2.unsqueeze(0)]
        
        # Check that all tokens are between 0 and 4096
        if (torch.any(codes[0] < 0) or torch.any(codes[0] > 4096) or 
            torch.any(codes[1] < 0) or torch.any(codes[1] > 4096) or 
            torch.any(codes[2] < 0) or torch.any(codes[2] > 4096)):
            return None

        with torch.inference_mode():
            audio_hat = model.decode(codes)

        audio_slice = audio_hat[0, :, 2048:4096]
        detached_audio = audio_slice.detach().cpu()
        audio_np = detached_audio.numpy()
        audio_int16 = (audio_np * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()
        return audio_bytes
        
    except Exception as e:
        print(f"Error converting tokens to audio: {e}")
        return None
