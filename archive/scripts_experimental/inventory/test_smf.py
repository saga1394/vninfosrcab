import httpx
import feedparser

r = httpx.get('https://smfederation.org.sg/feed/', verify=False, timeout=10)
fp = feedparser.parse(r.content)
print('SMF Feed entries:', len(fp.entries))
for e in fp.entries[:3]:
    print(f" - {e.title} | {e.published} | {e.link}")
