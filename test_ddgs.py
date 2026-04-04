import sys
try:
    from ddgs import DDGS
    print("Successfully imported DDGS from ddgs")
    results = DDGS().images("cats", max_results=2)
    print("Results:", list(results))
except Exception as e:
    print("Error:", type(e), e)
