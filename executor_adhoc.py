# %%
# PPT の文字起こし
from summarizer import PPTSummarizer, TextSummarizer

ppt_filepath = "data/sample.pptx"
text_summarizer = TextSummarizer()
ppt_summarizer = PPTSummarizer(text_summarizer)
result = ppt_summarizer.summarize(ppt_filepath)
print(result)

# %%
