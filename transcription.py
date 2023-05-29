from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import whisper

# Initialize tokenizer and model for spell checking
tokenizer = AutoTokenizer.from_pretrained("Bhuvana/t5-base-spellchecker")
model = AutoModelForSeq2SeqLM.from_pretrained("Bhuvana/t5-base-spellchecker")

# Function to correct spelling errors in a given input text
def correct(inputs):
    '''Corrects spelling errors in the input text using the spell checker model.
    
    Args:
        inputs (str): The input text to be spell-checked.
    
    Returns:
        str: The corrected version of the input text.
    '''
    # Encode the input text using the tokenizer
    input_ids = tokenizer.encode(inputs, return_tensors='pt')
    
    # Generate corrected output using the spell checker model
    sample_output = model.generate(
        input_ids,
        do_sample=True,
        max_length=50,
        top_p=0.99,
        num_return_sequences=1
    )
    
    # Decode the corrected output and remove special tokens
    res = tokenizer.decode(sample_output[0], skip_special_tokens=True)
    return res

# Load the whisper model for audio transcription
whisper_model = whisper.load_model("base")

# Function to transcribe audio file
def transcribe(audio_file):
    '''Transcribes the content of an audio file.
    
    Args:
        audio_file (str): The path to the audio file.
    
    Returns:
        str: The transcribed text from the audio file, with spelling errors corrected.
    '''
    # Load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(audio_file)
    audio = whisper.pad_or_trim(audio)

    # Convert audio data to PyTorch tensor and float data type
    mel = torch.from_numpy(audio).float()

    # Make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(mel).to(model.device)

    # Detect the spoken language using the whisper model
    _, probs = whisper_model.detect_language(mel)

    # Decode the audio using the whisper model
    options = whisper.DecodingOptions(fp16=False)
    result = whisper.decode(whisper_model, mel, options)
    result_text = result.text
    
    # Print the transcribed text
    print('result_text:' + result_text)

    # Correct any spelling errors in the transcribed text
    return correct(result_text)