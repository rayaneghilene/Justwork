import json, torch, time, logging, hashlib
from functools import lru_cache
from typing import Optional, List
from transformers import AutoModelForCausalLM, AutoTokenizer
import gc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

# Global variables for lazy loading
model = None
tokenizer = None
_model_loading = False

# In-memory cache for results (LRU cache with size limit)
result_cache = {}
MAX_CACHE_SIZE = 100

def get_cache_key(text: str, schema: str, examples: Optional[List[str]] = None) -> str:
    """Generate cache key for input parameters"""
    cache_input = f"{text}|{schema}|{examples or []}"
    return hashlib.md5(cache_input.encode()).hexdigest()

def cleanup_cache():
    """Remove oldest entries if cache is too large"""
    global result_cache
    if len(result_cache) > MAX_CACHE_SIZE:
        # Keep only the most recent MAX_CACHE_SIZE entries
        keys_to_remove = list(result_cache.keys())[:-MAX_CACHE_SIZE]
        for key in keys_to_remove:
            del result_cache[key]
        logger.info(f"🧹 Cache cleaned up, kept {MAX_CACHE_SIZE} entries")

def load_model_if_needed():
    """Lazy load model only when needed"""
    global model, tokenizer, _model_loading
    
    if model is not None and tokenizer is not None:
        return
    
    if _model_loading:
        logger.info("⏳ Model already loading, waiting...")
        while _model_loading:
            time.sleep(0.1)
        return
    
    logger.info("🔄 Loading NuExtract model (lazy loading)...")
    _model_loading = True
    model_load_start = time.time()
    
    try:
        # Load with optimizations
        model = AutoModelForCausalLM.from_pretrained(
            "numind/NuExtract-tiny", 
            trust_remote_code=True,
            torch_dtype=torch.float16 if device.type == 'cuda' else torch.float32,  # Use half precision on GPU
            device_map="auto" if device.type == 'cuda' else None
        )
        tokenizer = AutoTokenizer.from_pretrained("numind/NuExtract-tiny", trust_remote_code=True)
        
        if device.type != 'cuda':  # Only move to device if not using device_map
            model.to(device)
        
        model.eval()
        
        # Enable optimizations
        if hasattr(model, 'config'):
            model.config.pad_token_id = tokenizer.eos_token_id
        
        load_time = time.time() - model_load_start
        logger.info(f"✅ Model loaded and optimized in {load_time:.2f} seconds")
        logger.info(f"📊 Model info:")
        logger.info(f"   • Device: {device}")
        logger.info(f"   • Dtype: {model.dtype if hasattr(model, 'dtype') else 'unknown'}")
        logger.info(f"   • Memory usage: ~{torch.cuda.memory_allocated() / 1024**2:.0f}MB" if device.type == 'cuda' else "   • CPU model loaded")
        
    except Exception as e:
        logger.error(f"❌ Failed to load model: {str(e)}")
        raise
    finally:
        _model_loading = False

def predict_keywords(text: str, schema: str, examples: Optional[List[str]] = None) -> str:
    """Extract keywords with advanced optimizations and caching"""
    logger.info(f"🔍 Keyword prediction request:")
    logger.info(f"   • Text length: {len(text)} characters")
    logger.info(f"   • Schema length: {len(schema)} characters")
    logger.info(f"   • Examples: {len(examples) if examples else 0}")
    
    start_time = time.time()
    
    # Step 1: Check cache first
    cache_start = time.time()
    cache_key = get_cache_key(text, schema, examples)
    
    if cache_key in result_cache:
        result = result_cache[cache_key]
        logger.info(f"🎯 Cache HIT! Returned result in {time.time() - cache_start:.3f}s")
        logger.info(f"📊 Total time: {time.time() - start_time:.3f}s (cached)")
        return result
    
    logger.info(f"💾 Cache MISS, proceeding with generation...")
    
    # Step 2: Ensure model is loaded
    model_load_start = time.time()
    load_model_if_needed()
    if time.time() - model_load_start > 0.1:  # Only log if loading took time
        logger.info(f"⚡ Model loading: {time.time() - model_load_start:.2f}s")
    
    # Step 3: Prepare input with optimizations
    prep_start = time.time()
    
    if examples is None:
        examples = []
    
    # Clean and optimize schema
    try:
        schema_dict = json.loads(schema)
        schema = json.dumps(schema_dict, indent=2, separators=(',', ': '))  # More compact
    except json.JSONDecodeError:
        logger.warning(f"⚠️  Invalid JSON schema, using as-is")
    
    # Build improved prompt for NuExtract
    input_llm = "<|input|>\n### Template:\n" + schema + "\n"
    
    # Add examples more efficiently
    example_count = 0
    for i, example in enumerate(examples):
        if example and example.strip():
            try:
                example_dict = json.loads(example)
                input_llm += f"### Example:\n" + json.dumps(example_dict, indent=2) + "\n"
                example_count += 1
            except json.JSONDecodeError:
                logger.warning(f"⚠️  Invalid JSON example {i+1}, skipping")
    
    # If no examples provided, add a realistic example
    if example_count == 0:
        example_output = {
            "Skills": ["Python", "Machine Learning", "Data Analysis", "SQL"],
            "Job Titles": ["Data Scientist", "Software Engineer"],
            "Education": ["Master's in Computer Science", "Bachelor's in Mathematics"],
            "Projects": ["Customer Churn Prediction", "Recommendation System"],
            "Experience Years": ["5 years", "3+ years experience"]
        }
        input_llm += "### Example:\n" + json.dumps(example_output, indent=2) + "\n"
        logger.info("✓ Added default example for better model guidance")
    
    # Add text with length optimization
    text_preview = text[:100] + "..." if len(text) > 100 else text
    logger.info(f"📝 Text preview: {text_preview}")
    
    # Better text length management
    MAX_TEXT_LENGTH = 2500  # Leave more room for template and output
    if len(text) > MAX_TEXT_LENGTH:
        # Try to truncate at sentence boundaries
        sentences = text.split('. ')
        truncated_text = ""
        for sentence in sentences:
            if len(truncated_text + sentence + '. ') <= MAX_TEXT_LENGTH:
                truncated_text += sentence + '. '
            else:
                break
        
        if len(truncated_text) < MAX_TEXT_LENGTH * 0.8:  # If we lost too much, use simple truncation
            text = text[:MAX_TEXT_LENGTH]
        else:
            text = truncated_text.rstrip('. ')
        
        logger.warning(f"⚠️  Text truncated to {len(text)} characters (smart truncation)")
    
    input_llm += "### Text:\n" + text.strip() + "\n<|output|>\n"
    
    # Log the full prompt for debugging (first time only)
    if len(result_cache) == 0:  # Only log for first request to avoid spam
        logger.info("🔍 Full prompt preview:")
        prompt_preview = input_llm[:500] + "..." if len(input_llm) > 500 else input_llm
        logger.info(f"{prompt_preview}")
    
    # Tokenize with optimizations
    input_ids = tokenizer(
        input_llm, 
        return_tensors="pt", 
        truncation=True, 
        max_length=4000,
        padding=False  # No padding needed for single input
    ).to(device)
    
    input_length = input_ids.input_ids.shape[1]
    logger.info(f"✓ Input prepared: {input_length} tokens in {time.time() - prep_start:.2f}s")
    
    # Step 4: Generate with optimized parameters
    gen_start = time.time()
    
    with torch.no_grad():  # Disable gradients for inference
        try:
            # Optimized generation parameters for speed
            generation_config = {
                "max_new_tokens": 512,  # Limit output length
                "do_sample": False,     # Deterministic output (faster)
                "num_beams": 1,        # No beam search (faster)
                "pad_token_id": tokenizer.eos_token_id,
                "eos_token_id": tokenizer.eos_token_id,
                "use_cache": True,     # Enable KV cache
            }
            
            # Add temperature only if sampling
            if generation_config["do_sample"]:
                generation_config["temperature"] = 0.1
            
            logger.info(f"🤖 Starting generation with {len(generation_config)} optimized parameters...")
            
            outputs = model.generate(
                **input_ids,
                **generation_config
            )
            
            # Decode only the new tokens (more efficient)
            generated_tokens = outputs[0][input_ids.input_ids.shape[1]:]
            output = tokenizer.decode(generated_tokens, skip_special_tokens=True)
            
            logger.info(f"✓ Generation completed in {time.time() - gen_start:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {str(e)}")
            raise
        finally:
            # Clean up GPU memory if available
            if device.type == 'cuda':
                torch.cuda.empty_cache()
    
    # Step 5: Extract and validate result
    extract_start = time.time()
    
    logger.info(f"🔍 Raw model output preview: {output[:200]}...")
    
    # Handle different output formats with better parsing
    result = ""
    if "<|output|>" in output:
        if "<|end-output|>" in output:
            result = output.split("<|output|>")[1].split("<|end-output|>")[0].strip()
        else:
            # No end marker, take everything after <|output|>
            result = output.split("<|output|>")[1].strip()
    else:
        # No output markers, try to find JSON-like content
        logger.warning("⚠️  No <|output|> markers found, trying to extract JSON")
        
        # Look for JSON pattern (starts with { and ends with })
        start_idx = output.find('{')
        if start_idx != -1:
            # Find the matching closing brace
            brace_count = 0
            end_idx = start_idx
            for i, char in enumerate(output[start_idx:], start_idx):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break
            
            if brace_count == 0:
                result = output[start_idx:end_idx]
            else:
                logger.warning("⚠️  Could not find complete JSON in output")
                result = output.strip()
        else:
            logger.warning("⚠️  No JSON found in output, using full output")
            result = output.strip()
    
    # Clean up the result
    result = result.strip()
    
    # Validate and fix JSON
    try:
        parsed_result = json.loads(result)
        logger.info(f"✓ Valid JSON result extracted with {len(parsed_result)} fields")
        
        # Log what was actually extracted
        for key, value in parsed_result.items():
            if isinstance(value, list):
                logger.info(f"   • {key}: {len(value)} items")
            else:
                logger.info(f"   • {key}: {type(value).__name__}")
        
        # Ensure result is properly formatted
        result = json.dumps(parsed_result, indent=2, ensure_ascii=False)
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON result: {str(e)}")
        logger.error(f"Raw result: {result[:300]}...")
        
        # Try to fix common JSON issues
        try:
            # Remove any trailing commas
            fixed_result = result.replace(',}', '}').replace(',]', ']')
            
            # Try to parse again
            parsed_result = json.loads(fixed_result)
            result = json.dumps(parsed_result, indent=2, ensure_ascii=False)
            logger.info(f"✓ Fixed JSON result successfully")
            
        except json.JSONDecodeError:
            # Last resort: return empty schema
            logger.error(f"❌ Could not fix JSON, returning empty schema")
            schema_dict = json.loads(schema)
            result = json.dumps(schema_dict, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ Result extraction and validation: {time.time() - extract_start:.3f}s")
    
    # Step 6: Cache the result
    cache_store_start = time.time()
    result_cache[cache_key] = result
    cleanup_cache()  # Maintain cache size
    logger.info(f"💾 Result cached in {time.time() - cache_store_start:.3f}s")
    
    # Final summary
    total_time = time.time() - start_time
    logger.info(f"🎉 Keyword prediction completed:")
    logger.info(f"   • Total time: {total_time:.2f}s")
    logger.info(f"   • Result length: {len(result)} characters")
    logger.info(f"   • Cache entries: {len(result_cache)}")
    
    return result

def clear_cache():
    """Clear the result cache (useful for testing or memory management)"""
    global result_cache
    cache_size = len(result_cache)
    result_cache.clear()
    logger.info(f"🧹 Cache cleared: removed {cache_size} entries")

def get_cache_stats():
    """Get cache statistics"""
    return {
        "cache_size": len(result_cache),
        "max_cache_size": MAX_CACHE_SIZE,
        "cache_keys": list(result_cache.keys())[:5]  # First 5 keys for debugging
    }