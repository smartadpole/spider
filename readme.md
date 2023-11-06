# 爬虫
## 依赖环境
- python3   
	- selenium   
	- tqdm   
- chromdriver    
把 chromdriver 所在目录配置到环境变量即可；也可以修改脚本中的第一句话 `export PATH=[chromdriver_path]:$PATH`

## Github 项目爬取
根据关键字批量爬取 github 项目；    
>./search.sh 
## arXiv 网站每日更新论文爬取
爬取 arXiv 每日更新论文，导出成特定排版的 markdown 文本；    
>./new.sh 
> 
## arxiv 关键字 pdf 爬取
```angular2html
python arxiv/search_pdf.py --query low+light --output_dir $output

``` 
 

## issue
>Message: session not created: This version of ChromeDriver only supports Chrome version 78     

ChromeDriver与本地chrome浏览器的版本不一致导致     
根据 chrom 查找对应版本号 <https://blog.csdn.net/yoyocat915/article/details/80580066>     
ChromeDriver 下载地址 <http://npm.taobao.org/mirrors/chromedriver/>    
 


# TODO
- [ ] search_pdf.py 中舍弃 webdriver 的用法，用 requests 代替（顶会代码中有）；  
