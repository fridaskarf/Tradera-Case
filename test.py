import json

d = {
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "message": {
                "content": "Why did the tomato turn red?\n\nBecause it saw the salad dressing!",
                "role": "assistant",
            },
        }
    ],
    "created": 1684337449,
    "id": "chatcmpl-7HDOzJsRWxaD2TCLrdy0YP3I2P1Pk",
    "model": "gpt-3.5-turbo-0301",
    "object": "chat.completion",
    "usage": {"completion_tokens": 14, "prompt_tokens": 12, "total_tokens": 26},
}


print(d.get("choices")[0].get("message").get("content"))
