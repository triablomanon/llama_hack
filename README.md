# Llama API Client Project

This project demonstrates how to use the Llama API Client Python library to interact with Meta's Llama models.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API key:**
   Create a `.env` file in the root directory with your Llama API key:
   ```
   LLAMA_API_KEY=your_actual_api_key_here
   ```

3. **Get your API key:**
   - Visit [Meta's Llama API documentation](https://llama.developer.meta.com/docs)
   - Sign up and get your API key

## Usage

Run the API call:
```bash
python src/api_call.py
```

## Available Models

Some common Llama models you can use:
- `llama-3.1-8b-instruct`
- `llama-3.1-70b-instruct`
- `llama-3.1-405b-instruct`

## Error Handling

The code includes comprehensive error handling for:
- Authentication errors
- Rate limiting
- Connection issues
- API status errors

## Troubleshooting

If you get authentication errors:
1. Make sure your `.env` file exists and contains `LLAMA_API_KEY=your_key`
2. Verify your API key is valid
3. Check that you have sufficient credits/quota
