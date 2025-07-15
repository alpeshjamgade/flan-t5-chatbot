"""
Chat Engine - Core AI processing using FLAN-T5-Large
"""

import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from typing import List, Dict, Optional
from dataclasses import dataclass
import platform

from ..utils.logging import get_logger


@dataclass
class GenerationConfig:
    """Configuration for text generation"""
    max_length: int = 512
    min_length: int = 10
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.2
    do_sample: bool = True
    early_stopping: bool = True


class ChatEngine:
    """Core chat engine using FLAN-T5-Large"""

    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.model = None
        self.tokenizer = None
        self.device = self._detect_optimal_device()
        self.generation_config = GenerationConfig()
        self.max_context_length = 512

        self.logger.info(f"Initializing ChatEngine on device: {self.device}")

    def _detect_optimal_device(self):
        """Detect the optimal device based on system architecture"""
        system = platform.system().lower()
        machine = platform.machine().lower()

        self.logger.info(f"System: {system}, Architecture: {machine}")

        # Check for Apple Silicon (M1/M2/M3) on macOS
        if system == "darwin" and machine in ["arm64", "aarch64"]:
            try:
                # Check if MPS (Metal Performance Shaders) is available
                import torch
                if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    self.logger.info("Using Metal Performance Shaders (MPS) for Apple Silicon")
                    return torch.device("mps")
                else:
                    self.logger.warning("MPS not available, falling back to CPU")
                    return torch.device("cpu")
            except Exception as e:
                self.logger.warning(f"Error checking MPS availability: {e}")
                return torch.device("cpu")

        # Check for CUDA on other systems
        elif torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            self.logger.info(f"Using CUDA GPU: {gpu_name}")
            return torch.device("cuda")

        # Fallback to CPU
        else:
            self.logger.info("Using CPU (no GPU acceleration available)")
            return torch.device("cpu")

    def load_model(self):
        """Load FLAN-T5-Large model and tokenizer"""
        model_name = self.config.model.name

        self.logger.info(f"Loading model: {model_name}")

        # Load tokenizer
        self.tokenizer = T5Tokenizer.from_pretrained(
            model_name,
            legacy=False
        )

        # Set pad token to eos token to avoid attention mask issues
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Determine dtype based on device
        if self.device.type == "cuda":
            dtype = torch.float16
            device_map = "auto"
        elif self.device.type == "mps":
            # MPS works better with float32 for T5 models
            dtype = torch.float32
            device_map = None
        else:
            dtype = torch.float32
            device_map = None

        # Load model
        self.model = T5ForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=dtype,
            device_map=device_map
        )

        # Move to device if not using device_map
        if device_map is None:
            self.model = self.model.to(self.device)

        self.model.eval()

        # Update generation config from settings
        self._update_generation_config()

        # Warm up the model
        self._warmup_model()

        self.logger.info("Model loaded and warmed up successfully")

    def _update_generation_config(self):
        """Update generation config from settings"""
        model_config = self.config.model
        self.generation_config.max_length = model_config.max_length
        self.generation_config.temperature = model_config.temperature
        self.generation_config.top_p = model_config.top_p
        self.generation_config.top_k = model_config.top_k
        self.generation_config.repetition_penalty = model_config.repetition_penalty
        self.generation_config.do_sample = model_config.do_sample

    def _warmup_model(self):
        """Warm up the model with a simple query"""
        self.logger.debug("Warming up model...")

        try:
            warmup_prompt = "Answer the following question: What is 2+2?"

            inputs = self.tokenizer(
                warmup_prompt,
                return_tensors="pt",
                max_length=100,
                truncation=True,
                padding=True,
                return_attention_mask=True
            )

            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                _ = self.model.generate(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs['attention_mask'],
                    max_new_tokens=10,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )

            self.logger.debug("Model warmup completed")
        except Exception as e:
            self.logger.warning(f"Model warmup failed: {e}")

    def generate_response(self, user_input: str, context: List[Dict] = None) -> str:
        """Generate response using FLAN-T5"""
        try:
            self.logger.debug(f"Generating response for input: {user_input[:50]}...")

            # Prepare the prompt with context
            prompt = self._prepare_prompt(user_input, context)

            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=self.max_context_length,
                truncation=True,
                padding=True,
                return_attention_mask=True
            )

            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs['attention_mask'],
                    max_new_tokens=100,
                    min_length=5,
                    temperature=self.generation_config.temperature,
                    top_p=self.generation_config.top_p,
                    top_k=self.generation_config.top_k,
                    repetition_penalty=self.generation_config.repetition_penalty,
                    do_sample=self.generation_config.do_sample,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=3
                )

            # Decode response
            response = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )

            # Post-process response
            response = self._post_process_response(response, prompt)

            self.logger.debug(f"Generated response: {response[:50]}...")
            return response

        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Could you please try rephrasing your question?"

    def _prepare_prompt(self, user_input: str, context: List[Dict] = None) -> str:
        """Prepare the prompt with context for FLAN-T5"""

        # FLAN-T5 works best with clear instruction formats
        # Build context if available
        context_str = ""
        if context and len(context) > 0:
            # Get last few messages for context
            recent_context = context[-4:] if len(context) > 4 else context
            context_parts = []

            for msg in recent_context:
                if msg["role"] == "user":
                    context_parts.append(f"User: {msg['content']}")
                elif msg["role"] == "assistant":
                    context_parts.append(f"Assistant: {msg['content']}")

            if context_parts:
                context_str = "Previous conversation:\n" + "\n".join(context_parts) + "\n\n"

        # Create the instruction prompt
        prompt = f"{context_str}You are a helpful AI assistant. Please respond naturally and conversationally to the following message:\n\nUser: {user_input}\nAssistant:"

        return prompt

    def _post_process_response(self, response: str, original_prompt: str) -> str:
        """Post-process the generated response"""

        # Remove the original prompt from response if it appears
        if original_prompt in response:
            response = response.replace(original_prompt, "").strip()

        # Clean up common artifacts
        lines = response.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Remove conversation markers if they appear at the start
            if line.startswith("Assistant:"):
                line = line[10:].strip()
            elif line.startswith("User:"):
                continue  # Skip user lines in response

            # Skip lines that are just instruction repetitions
            skip_phrases = [
                "You are a helpful AI assistant",
                "Please respond naturally",
                "Previous conversation:",
                "respond to the following message"
            ]

            if not any(phrase.lower() in line.lower() for phrase in skip_phrases):
                cleaned_lines.append(line)

        # Join the cleaned lines
        response = ' '.join(cleaned_lines).strip()

        # If response is empty or too short, return a minimal fallback
        if not response or len(response) < 2:
            response = "I understand."

        # Ensure proper capitalization
        if response and response[0].islower():
            response = response[0].upper() + response[1:]

        return response

    def update_generation_config(self, **kwargs):
        """Update generation configuration"""
        for key, value in kwargs.items():
            if hasattr(self.generation_config, key):
                setattr(self.generation_config, key, value)
                self.logger.debug(f"Updated generation config: {key} = {value}")

    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up ChatEngine resources")
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer

        # Clear cache based on device type
        if self.device.type == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif self.device.type == "mps":
            # MPS doesn't have a direct cache clearing method, but this helps
            if hasattr(torch.mps, 'empty_cache'):
                torch.mps.empty_cache()

        # General cleanup
        import gc
        gc.collect()
