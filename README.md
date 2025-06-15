# Hệ thống RAG hỗ trợ sinh mã chiến lược giao dịch với LLM

## 📝 Giới thiệu

Dự án này xây dựng một hệ thống **Retrieval-Augmented Generation (RAG)** sử dụng Large Language Models (LLM) để tự động sinh mã Python cho các chiến lược giao dịch tài chính. Người dùng chỉ cần cung cấp mô tả chiến lược bằng ngôn ngữ tự nhiên, hệ thống sẽ dựa trên kiến thức từ một thư viện phân tích kỹ thuật (trong ví dụ này là `pandas-ta`) để tạo ra mã nguồn hoàn chỉnh.

Mục tiêu chính là giảm thiểu thời gian và công sức cho các nhà giao dịch và nhà phát triển trong việc lập trình các chiến lược phức tạp, đồng thời đảm bảo mã được sinh ra tuân thủ đúng các hàm và tham số của thư viện cơ sở.

## 💡 Ý tưởng cốt lõi

Kiến trúc của dự án dựa trên mô hình RAG, một kỹ thuật tiên tiến trong lĩnh vực xử lý ngôn ngữ tự nhiên, kết hợp hai thành phần chính:

1.  **Retrieval (Truy xuất)**: Hệ thống bắt đầu bằng việc thu thậpและlưu trữ kiến thức từ một codebase cụ thể (ví dụ: toàn bộ mã nguồn của thư viện `pandas-ta`). Dữ liệu này được chia nhỏ, chuyển đổi thành các vector embedding và được lưu trữ trong một cơ sở dữ liệu vector chuyên dụng (`pgvector`). Khi nhận được yêu cầu từ người dùng, hệ thống sẽ truy xuất các đoạn mã hoặc tài liệu liên quan nhất từ cơ sở dữ liệu này.

2.  **Generation (Sinh)**: Các thông tin được truy xuất sẽ được sử dụng làm "ngữ cảnh" bổ sung và cung cấp cho LLM cùng với prompt ban đầu của người dùng. Dựa trên ngữ cảnh này, LLM sẽ sinh ra mã Python chính xác và phù hợp với yêu cầu.

Cách tiếp cận này giúp LLM "học" và áp dụng đúng cú pháp của một thư viện cụ thể mà không cần phải huấn luyện lại từ đầu, tăng cường độ chính xác và giảm thiểu lỗi "ảo giác" (hallucination).

## 🚀 Luồng hoạt động (Pipeline)

Hệ thống hoạt động qua hai giai đoạn chính: **Tiền xử lý** và **Suy luận**.

### Giai đoạn 1: Tiền xử lý (Script: `preprocess.py`)

Giai đoạn này chuẩn bị cơ sở kiến thức cho hệ thống RAG.

1.  **Thu thập dữ liệu (Ingestion)**: Script `gitingest` được sử dụng để thu thập toàn bộ mã nguồn từ một kho Git (local hoặc remote URL). Kết quả được lưu vào file `data/source.txt`.
2.  **Phân đoạn (Chunking)**: `src/preprocessing/chunk_splitter.py` đọc file `source.txt` và chia nhỏ mã nguồn thành các đoạn (chunks) hợp lý dựa trên cấu trúc thư mục. Các chunks được lưu tại `data/data_chunks.json`.
3.  **Tạo Ngữ cảnh (Context Generation)**: `src/agents/contextual_agent.py` được sử dụng để tạo ra một bản tóm tắt ngắn gọn cho mỗi chunk, cung cấp ngữ cảnh về vị trí file và các công nghệ chính. Dữ liệu sau khi làm giàu ngữ cảnh được lưu tại `data/final_data.json`.
4.  **Tạo Embeddings và Lưu trữ**: Script `src/embeddings.py` đọc `final_data.json`, sử dụng một mô hình embedding của OpenAI (`text-embedding-3-small`) để chuyển đổi các chunk thành vector, và lưu trữ chúng vào cơ sở dữ liệu PostgreSQL với extension `pgvector`.

### Giai đoạn 2: Suy luận (Script: `main.py`)

Đây là giai đoạn người dùng tương tác với hệ thống để nhận mã.

1.  **Người dùng cung cấp Prompt**: Người dùng mô tả chi tiết chiến lược giao dịch bằng ngôn ngữ tự nhiên.
2.  **Truy xuất thông tin (Retrieval)**: `src/agents/rag_agent.py` nhận prompt, tạo embedding cho prompt đó và truy vấn cơ sở dữ liệu `pgvector` để tìm các chunk mã nguồn có liên quan nhất.
3.  **Sinh mã (Code Generation)**: Các chunk được truy xuất đượcส่งไปยัง LLM (ví dụ: `gpt-3.5-turbo`) cùng với prompt gốc. LLM sử dụng ngữ cảnh này để tạo ra đoạn mã Python hoàn chỉnh cho chiến lược.
4.  **Streaming**: Kết quả được trả về cho người dùng dưới dạng một luồng (stream) để cải thiện trải nghiệm.

## 📂 Cấu trúc thư mục


├── data/ # Lưu trữ dữ liệu nguồn và các file đã qua xử lý
├── docs/ # Tài liệu dự án
├── examples/ # Các kịch bản ví dụ
├── pandas_ta/ # Bản sao của thư viện pandas-ta làm cơ sở kiến thức
├── src/
│ ├── agents/ # Chứa các agent LLM (RAG và Contextual)
│ ├── core/ # Quản lý cấu hình và kết nối cơ sở dữ liệu
│ ├── preprocessing/ # Các script tiền xử lý dữ liệu
│ └── embeddings.py # Script tạo và lưu trữ embeddings
├── tests/ # Các bài kiểm tra cho thư viện pandas-ta
├── main.py # Điểm vào chính của ứng dụng
├── preprocess.py # Script chạy toàn bộ pipeline tiền xử lý
├── pyproject.toml # Định nghĩa các dependencies của dự án
└── README.md # Tài liệu hướng dẫn
## 🛠️ Cài đặt và Sử dụng

### Yêu cầu
* Python 3.10+
* PostgreSQL với extension `pgvector` đã được cài đặt và đang chạy.
* Một API key của OpenAI

### Các bước cài đặt

1.  **Clone a Repositório:**
   ```bash
   git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
   cd your-repo-name
   ```

2.  **Cài đặt các Dependencies:**
   Dự án sử dụng Poetry để quản lý các gói. Cài đặt các gói cần thiết:
   ```bash
   pip install poetry
   poetry install
   ```

3.  **Thiết lập Môi trường:**
   Tạo file `.env` ở thư mục gốc và điền các thông tin cần thiết:
   ```env
   DATABASE_URL="postgresql://user:password@hostname:5432/vector_db"
   OPENAI_API_KEY="sk-your-openai-api-key"
   MAX_TOKENS_PER_MINUITE=250000
   ```
   *Lưu ý: Thay thế `user`, `password`, `hostname` bằng thông tin xác thực của cơ sở dữ liệu PostgreSQL của bạn.*

4.  **Chuẩn bị Cơ sở dữ liệu:**
   Dự án này yêu cầu một cơ sở dữ liệu PostgreSQL đã được cài đặt và kích hoạt extension `pgvector`.
   
   a. **Cài đặt PostgreSQL**: Cài đặt PostgreSQL trên hệ thống của bạn (nếu chưa có).
   b. **Cài đặt `pgvector`**: Làm theo hướng dẫn tại [kho lưu trữ `pgvector`](https://github.com/pgvector/pgvector) để cài đặt extension.
   c. **Tạo cơ sở dữ liệu**: Tạo một cơ sở dữ liệu mới cho dự án (ví dụ: `vector_db`).
   d. **Kích hoạt extension**: Kết nối đến cơ sở dữ liệu vừa tạo và chạy lệnh SQL: `CREATE EXTENSION IF NOT EXISTS vector;`
   e. **Cập nhật file `.env`**: Đảm bảo rằng biến `DATABASE_URL` trong file `.env` của bạn trỏ đúng đến cơ sở dữ liệu vừa thiết lập.

5.  **Chạy Pipeline Tiền xử lý:**
   Chạy script `preprocess.py` để chuẩn bị dữ liệu cho RAG. Lần đầu tiên, bạn cần cung cấp đường dẫn đến thư viện `pandas-ta`.
   ```bash
   python preprocess.py --source ./pandas_ta
   ```
   Quá trình này có thể mất vài phút tùy thuộc vào giới hạn TPM của API key.

6.  **Chạy Chương trình Chính:**
   Sau khi tiền xử lý hoàn tất, bạn có thể chạy `main.py` để bắt đầu sinh mã.
   ```bash
   python main.py
   ```
   Chương trình sẽ sử dụng prompt được hardcode để demo. Bạn có thể thay đổi prompt trong `main.py` để thử các chiến lược khác.

## ✨ Ví dụ

**Prompt đầu vào (trong `main.py`):**
```python
"""
Chiến Lược Giao Dịch: "Sóng Lượng Tử SINWMA"
Chiến lược này khai thác dao động và độ dốc của đường SINWMA để xác định các điểm vào và ra khỏi thị trường, tập trung vào sự thay đổi động lượng và xu hướng ngắn hạn.

Chỉ báo sử dụng:
SINWMA(14): Đường trung bình động trọng số Sine với chu kỳ 14.
SINWMA(28): Đường trung bình động trọng số Sine với chu kỳ 28.

Logic Giao Dịch
Điều kiện Mua (Long):
- Đường SINWMA(14) cắt lên trên đường SINWMA(28).
- Độ dốc của đường SINWMA(14) phải là dương.
- Giá đóng cửa của nến tín hiệu phải cao hơn SINWMA(14).

Điều kiện Bán (Short):
- Đường SINWMA(14) cắt xuống dưới đường SINWMA(28).
- Độ dốc của đường SINWMA(14) phải là âm.
- Giá đóng cửa của nến tín hiệu phải thấp hơn SINWMA(14).

Điều kiện Đóng Lệnh Mua (Close Long):
- Đường SINWMA(14) cắt xuống dưới đường SINWMA(28).

Điều kiện Đóng Lệnh Bán (Close Short):
- Đường SINWMA(14) cắt lên trên đường SINWMA(28).
"""

Kết quả mã Python được sinh ra (dự kiến):
import pandas as pd
import pandas_ta as ta
from typing import DataFrame

def sinwma_quantum_wave_strategy(df: pd.DataFrame, sinwma_fast_period: int = 14, sinwma_slow_period: int = 28) -> pd.DataFrame:
   df[f'SINWMA_{sinwma_fast_period}'] = ta.sinwma(df['Close'], length=sinwma_fast_period)
   df[f'SINWMA_{sinwma_slow_period}'] = ta.sinwma(df['Close'], length=sinwma_slow_period)
   df['SINWMA_14_SLOPE'] = df[f'SINWMA_{sinwma_fast_period}'].diff()
   
   long_condition = (
       (df[f'SINWMA_{sinwma_fast_period}'] > df[f'SINWMA_{sinwma_slow_period}']) &
       (df[f'SINWMA_{sinwma_fast_period}'].shift(1) <= df[f'SINWMA_{sinwma_slow_period}'].shift(1)) &
       (df['SINWMA_14_SLOPE'] > 0) &
       (df['Close'] > df[f'SINWMA_{sinwma_fast_period}'])
   )
   
   short_condition = (
       (df[f'SINWMA_{sinwma_fast_period}'] < df[f'SINWMA_{sinwma_slow_period}']) &
       (df[f'SINWMA_{sinwma_fast_period}'].shift(1) >= df[f'SINWMA_{sinwma_slow_period}'].shift(1)) &
       (df['SINWMA_14_SLOPE'] < 0) &
       (df['Close'] < df[f'SINWMA_{sinwma_fast_period}'])
   )
   
   close_long_condition = (
       (df[f'SINWMA_{sinwma_fast_period}'] < df[f'SINWMA_{sinwma_slow_period}']) &
       (df[f'SINWMA_{sinwma_fast_period}'].shift(1) >= df[f'SINWMA_{sinwma_slow_period}'].shift(1))
   )
   
   close_short_condition = (
       (df[f'SINWMA_{sinwma_fast_period}'] > df[f'SINWMA_{sinwma_slow_period}']) &
       (df[f'SINWMA_{sinwma_fast_period}'].shift(1) <= df[f'SINWMA_{sinwma_slow_period}'].shift(1))
   )
   
   df['Signal'] = 0
   long = False
   short = False
   
   for i in range(1, len(df)):
       if long_condition[i] and not long:
           df.loc[i, 'Signal'] = 1
           long = True
           short = False
       elif short_condition[i] and not short:
           df.loc[i, 'Signal'] = -1
           long = False
           short = True
       elif close_long_condition[i] and long:
           df.loc[i, 'Signal'] = 2
           long = False
       elif close_short_condition[i] and short:
           df.loc[i, 'Signal'] = 2
           short = False
           
   return df

if __name__ == "__main__":
   # Example Usage:
   # Create a sample DataFrame (replace with your actual data)
   data = {
       'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', 
                              '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10',
                              '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-14', '2023-01-15',
                              '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19', '2023-01-20']),
       'Open': [100, 102, 101, 103, 105, 104, 106, 107, 108, 109, 110, 108, 107, 105, 103, 101, 100, 98, 99, 100],
       'High': [103, 104, 103, 106, 107, 106, 108, 109, 110, 111, 112, 110, 109, 107, 105, 103, 102, 100, 101, 102],
       'Low': [99, 101, 100, 102, 104, 103, 105, 106, 107, 108, 109, 107, 106, 104, 102, 100, 99, 97, 98, 99],
       'Close': [102, 103, 102, 105, 106, 105, 107, 108, 109, 110, 111, 109, 108, 106, 104, 102, 101, 99, 100, 101],
       'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900]
   }
   df = pd.DataFrame(data)
   df.set_index('Date', inplace=True)
   
   # Apply the strategy
   result_df = sinwma_quantum_wave_strategy(df)
   print(result_df)