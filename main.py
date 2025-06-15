#!/usr/bin/env python3

import asyncio
import time
from collections.abc import Generator

from src.agents.rag_agent import stream_messages

async def stream_response(prompt: str) -> list[str]:
    """
    Invoke an async generator from the RAG agent and collect the resulting chunks into a list.
    """
    message_chunks: list[str] = []
    async for chunk in stream_messages(prompt):
        message_chunks.append(chunk)
    return message_chunks

def stream_sync(prompt: str) -> Generator[str, None, None]:
    """
    Synchronize the AsyncGenerator so that it can be iterated sequentially.
    """
    # Run the event loop and collect all results.
    messages = asyncio.run(stream_response(prompt))

    # Return each chunk with a delay (simulating streaming).
    for message in messages:
        yield message
        time.sleep(0.05)

def main():
    # Hardcode prompt
    prompt = """
Write Python code for the following strategy (based on OHLCV data with columns ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']):
Chiến Lược Giao Dịch: "Sóng Lượng Tử SINWMA"
Chiến lược này khai thác dao động và độ dốc của đường SINWMA để xác định các điểm vào và ra khỏi thị trường, tập trung vào sự thay đổi động lượng và xu hướng ngắn hạn.

Chỉ báo sử dụng:
SINWMA(14): Đường trung bình động trọng số Sine với chu kỳ 14.
SINWMA(28): Đường trung bình động trọng số Sine với chu kỳ 28.
Logic Giao Dịch
Điều kiện Mua (Long):

Đường SINWMA(14) cắt lên trên đường SINWMA(28).
Độ dốc của đường SINWMA(14) phải là dương, được tính bằng công thức: Slope(SINWMA(14), 1) > 0. Điều này xác nhận động lượng tăng đang hình thành.
Trong đó: Slope(SINWMA(14), 1) = SINWMA(14) hiện tại - SINWMA(14) của nến trước đó.
Giá đóng cửa của nến tín hiệu phải cao hơn SINWMA(14).
Điều kiện Bán (Short):

Đường SINWMA(14) cắt xuống dưới đường SINWMA(28).
Độ dốc của đường SINWMA(14) phải là âm, được tính bằng công thức: Slope(SINWMA(14), 1) < 0. Điều này xác nhận động lượng giảm đang hình thành.
Trong đó: Slope(SINWMA(14), 1) = SINWMA(14) hiện tại - SINWMA(14) của nến trước đó.
Giá đóng cửa của nến tín hiệu phải thấp hơn SINWMA(14).
Điều kiện Đóng Lệnh Mua (Close Long):

Đường SINWMA(14) cắt xuống dưới đường SINWMA(28).
Điều kiện Đóng Lệnh Bán (Close Short):

Đường SINWMA(14) cắt lên trên đường SINWMA(28).

The code should:
-Receive a pandas DataFrame as input, along with parameters for customization (**Utilize Python type hints for all its parameters and its return type.**).
- Use pandas-ta library for technical indicators. In case it is not available, perform detailed calculations.
-Create a 'Signal' column with values 1 (buy), -1 (sell), 0 (no trade), 2 (close position (long, short)).
-Use 'long' (True/False) and 'short' (True/False) variables to track position status. When 'Signal' = 1, long = True and short = False; when 'Signal' = -1, long = False and short = True.
-Return the DataFrame with the added 'Signal' column.
-Include an #Example Usage section (if applicable) within an if __name__ == "__main__" block.
-Name the strategy execution function with the suffix "_strategy" (for easy strategy execution).
""" 
    
    print(f">>> Prompt: {prompt}\n")
    print(">>> Assistant trả lời (streaming):\n")
    for chunk in stream_sync(prompt):
        # in ngay lập tức từng chunk ra stdout
        print(chunk, end="", flush=True)
    print()  # xuống dòng cuối cùng

if __name__ == "__main__":
    main()
