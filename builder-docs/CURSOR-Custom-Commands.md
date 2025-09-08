# Cursor Custom Commands for Code Builder

This guide shows how to set up Cursor Custom Commands to automatically POST evaluation responses to the Code Builder server.

## Setup

### 1. Create Custom Commands

In Cursor, go to **Settings > Custom Commands** and add these commands:

#### Command 1: Post Evaluation Response
- **Name**: `Post Evaluation Response`
- **Command**: 
```bash
curl -X POST http://127.0.0.1:5000/response/{{EVAL_ID}} \
  -H "Content-Type: application/json" \
  -d '{{CURSOR_SELECTION}}'
```
- **Keybinding**: `Ctrl+Shift+E` (or your preference)

#### Command 2: Post ABC Evaluation Response
- **Name**: `Post ABC Evaluation Response`
- **Command**:
```bash
curl -X POST http://127.0.0.1:5000/response/{{EVAL_ID}} \
  -H "Content-Type: application/json" \
  -d '{{CURSOR_SELECTION}}'
```
- **Keybinding**: `Ctrl+Shift+A` (or your preference)

### 2. Manual Setup (Alternative)

If you prefer manual setup, you can:

1. **Copy the evaluation prompt** from the server URL
2. **Paste it into Cursor Chat or Composer**
3. **Get the JSON response** from Cursor
4. **POST it manually** using curl:

```bash
# Replace EVAL_ID with the actual evaluation ID from the server
curl -X POST http://127.0.0.1:5000/response/abc12345 \
  -H "Content-Type: application/json" \
  -d '{
    "overall_score": 85,
    "dimensions": {
      "clarity": 90,
      "design": 80,
      "maintainability": 85
    },
    "reasoning": "Good code with clear structure"
  }'
```

## Usage Workflow

### Single File Evaluation

1. **Start the server**:
   ```bash
   python builder/cli.py eval:objective src/hello.ts --server
   ```

2. **Copy the prompt URL** from the terminal output

3. **Open the URL** in your browser to see the evaluation prompt

4. **Copy the prompt** and paste it into Cursor Chat

5. **Get Cursor's JSON response** and select it

6. **Run the Custom Command** (`Ctrl+Shift+E`) to POST the response

7. **The evaluation completes automatically** and shows the final score

### ABC Iteration Evaluation

1. **Start the server**:
   ```bash
   python builder/cli.py iter:cursor src/hello.ts --server
   ```

2. **Follow the same steps** as single evaluation

3. **Use the ABC Custom Command** (`Ctrl+Shift+A`) for ABC responses

## Response Format

The JSON response should follow this format:

### Single Evaluation Response
```json
{
  "overall_score": 85,
  "dimensions": {
    "clarity": 90,
    "design": 80,
    "maintainability": 85,
    "tests": 75,
    "rule_compliance": 95
  },
  "reasoning": "Detailed explanation of the evaluation"
}
```

### ABC Evaluation Response
```json
{
  "variant_scores": {
    "A": {
      "overall_score": 80,
      "dimensions": {
        "clarity": 85,
        "design": 75
      }
    },
    "B": {
      "overall_score": 90,
      "dimensions": {
        "clarity": 95,
        "design": 85
      }
    },
    "C": {
      "overall_score": 70,
      "dimensions": {
        "clarity": 75,
        "design": 65
      }
    }
  },
  "winner": "B",
  "confidence": 0.85,
  "reasoning": "B is the best variant because..."
}
```

## Troubleshooting

### Server Not Running
- Make sure the server is started with `--server` flag
- Check that port 5000 is available
- Look for error messages in the terminal

### Evaluation Not Found
- Verify the evaluation ID is correct
- Check that the evaluation was created successfully
- Look at the server logs for errors

### JSON Parse Error
- Ensure the JSON is valid
- Check that all required fields are present
- Verify the Content-Type header is set to `application/json`

### Connection Refused
- Make sure the server is running on `127.0.0.1:5000`
- Check firewall settings
- Try using `localhost` instead of `127.0.0.1`

## Advanced Usage

### Custom Server Host/Port
If you need to use a different host or port:

1. **Start server with custom settings**:
   ```bash
   python builder/scripts/cursor_server.py --host 0.0.0.0 --port 8080
   ```

2. **Update Custom Commands** to use the new URL:
   ```bash
   curl -X POST http://0.0.0.0:8080/response/{{EVAL_ID}} \
     -H "Content-Type: application/json" \
     -d '{{CURSOR_SELECTION}}'
   ```

### Multiple Evaluations
The server can handle multiple evaluations simultaneously. Each evaluation gets a unique ID and can be accessed independently.

### Server Status
Visit `http://127.0.0.1:5000/` to see:
- Server status
- Active evaluations
- API documentation
- Evaluation history

## Integration with CI

The server can also be used in CI environments:

1. **Start server in background**:
   ```bash
   python builder/scripts/cursor_server.py &
   ```

2. **Create evaluations** via API:
   ```bash
   curl -X POST http://127.0.0.1:5000/evaluate \
     -H "Content-Type: application/json" \
     -d '{"path": "src/hello.ts", "type": "single"}'
   ```

3. **Get evaluation results**:
   ```bash
   curl http://127.0.0.1:5000/result/EVAL_ID
   ```

This makes it easy to integrate Code Builder evaluation into automated workflows while still allowing human evaluation via Cursor.
