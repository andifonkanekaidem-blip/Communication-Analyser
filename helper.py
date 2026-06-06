import aiofiles
import json
async def read_questions()->list:
    async with aiofiles.open('questions.json',mode='r') as f:
        content = await f.read()
        data = json.loads(content)
        return data