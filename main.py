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
Ý TƯỞNG GIAO DỊCH: "Momentum Hội Tụ Xu Hướng"
Chiến lược này tìm kiếm các điểm vào lệnh thuận theo xu hướng chính, được kích hoạt bởi tín hiệu từ một chỉ báo dao động nhạy và được lọc bởi sức mạnh của xu hướng.

Các Chỉ Báo Sử Dụng
Lọc Xu Hướng (Trend Filter):

EMA(50): Đường trung bình động hàm mũ chu kỳ 50.
EMA(200): Đường trung bình động hàm mũ chu kỳ 200.
Tín Hiệu Động Lượng (Momentum Signal):

QQE (Quantitative Qualitative Estimation): Sử dụng các tham số mặc định (length=14, smoothing=5, factor=4.236). Chỉ báo này bao gồm:
Đường QQE (QQE_14_5_4.236): Đường tín hiệu chính.
Đường Signal (QQEl_14_5_4.236): Đường tín hiệu của QQE.
Mức 50: Ngưỡng xác định phe Bull/Bear.
Xác Nhận Sức Mạnh Xu Hướng (Trend Strength Confirmation):

ADX (Average Directional Movement Index): Sử dụng chu kỳ 14 (length=14).
Lô Gic Giao Dịch
Lệnh Mua (Long Entry)
Vào lệnh Mua khi TẤT CẢ các điều kiện sau được thỏa mãn đồng thời:

Xu Hướng Tăng Dài Hạn: Giá đóng cửa hiện tại cao hơn đường EMA 200.
Xu Hướng Tăng Trung Hạn: Đường EMA 50 nằm trên đường EMA 200.
Xu Hướng Có Sức Mạnh: Chỉ số ADX(14) lớn hơn 23.
ADX14 > 23
Tín Hiệu Mua: Đường QQE cắt lên trên đường Signal của nó.
Xác Nhận Động Lượng: Tại thời điểm cắt lên, đường QQE phải đang ở trên mức 50.

Lệnh Bán (Short Entry)
Vào lệnh Bán khi TẤT CẢ các điều kiện sau được thỏa mãn đồng thời:
Xu Hướng Giảm Dài Hạn: Giá đóng cửa hiện tại thấp hơn đường EMA 200.
 
Xu Hướng Giảm Trung Hạn: Đường EMA 50 nằm dưới đường EMA 200.
 
Xu Hướng Có Sức Mạnh: Chỉ số ADX(14) lớn hơn 23.

Tín Hiệu Bán: Đường QQE cắt xuống dưới đường Signal của nó.

Xác Nhận Động Lượng: Tại thời điểm cắt xuống, đường QQE phải đang ở dưới mức 50.

Đóng Vị Thế (Position Close)
Đóng Lệnh Mua: Khi đường QQE cắt xuống dưới đường Signal của nó.
Đóng Lệnh Bán: Khi đường QQE cắt lên trên đường Signal của nó.

The code should:
-Receive a pandas DataFrame as input, along with parameters for customization (**Utilize Python type hints for all its parameters and its return type.**).
-Use pandas-ta library for technical indicators. In case it is not available, perform detailed calculations.
-Create a 'Signal' column with values 1 (buy), -1 (sell), 0 (no trade), 2 (close position (long, short)).
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
