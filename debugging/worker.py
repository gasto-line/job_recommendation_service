import sys, json, fasttext
from fake_model import FakeFastTextModel

model_path = sys.argv[1]

if "lang" in model_path:
    print("Loading model to memory")
    model = fasttext.load_model(model_path)
    print("Model loaded")

else:
    model = FakeFastTextModel()

payload = json.load(sys.stdin)
# payload contains list of texts / tokens ...

if "lang" in model_path:
    result = {"FR": [[],[]], "EN": [[],[]]}
    for i,text in enumerate(payload):
        full_text=" ".join(text)
        lang = model.predict(full_text)[0][0]
        if lang == "__label__fra_Latn":
            result["FR"][0].append(i)
            result["FR"][1].append(text)
        elif lang == "__label__eng_Latn":
            result["EN"][0].append(i)
            result["EN"][1].append(text)
else:
    result = {"embeddings": []}
    for text in payload:
        result["embeddings"].append([model.get_word_vector(token).tolist() for token in text])

print(json.dumps(result))
# process exits -> memory freed