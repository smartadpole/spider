# arXiv ID 查找器

根据论文名称自动搜索对应的 arXiv ID

## 功能特点

- 自动清理论文名称（去除.pdf、.txt、下划线等）
- 使用 arXiv API 搜索论文
- 输出两段格式：第一段是所有 arXiv ID，第二段是失败的文献名字
- 支持直接打印到控制台或保存到文件

## 使用方法

### 直接打印到控制台（推荐）
```bash
python3 arxiv_id_finder.py input_file.txt
```

### 保存到文件
```bash
python3 arxiv_id_finder.py input_file.txt -o output_file.txt
```

### 调整请求间隔
```bash
python3 arxiv_id_finder.py input_file.txt -d 2.0
```

## 输出格式

### 控制台输出
```
==================================================
找到的 arXiv ID:
1706.03762
2405.04807
1810.04805
2105.07926
1506.04449

搜索失败的文献名字:
paper_ResNet_Deep_Residual_Learning.pdf
GPT_Improving_Language_Understanding_by_Generative_Pre-Training
YOLO_You_Only_Look_Once
==================================================
```

### 文件输出
```
找到的 arXiv ID:
1706.03762
2405.04807
1810.04805
2105.07926
1506.04449

搜索失败的文献名字:
paper_ResNet_Deep_Residual_Learning.pdf
GPT_Improving_Language_Understanding_by_Generative_Pre-Training
YOLO_You_Only_Look_Once
```

## 参数说明

- `input_file`: 包含论文名称的输入文件（必需）
- `-o, --output`: 输出文件路径（可选，默认直接打印到控制台）
- `-d, --delay`: 请求间隔时间，单位秒（默认: 1.0）

## 依赖要求

```bash
pip install requests
```

## 示例

```bash
# 使用示例文件测试
python3 arxiv_id_finder.py sample_titles.txt
``` 