from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
import base64

endpoint ="https://risorsa-per-ocr.cognitiveservices.azure.com/"
key = ""

model_id = "ocr-sdo-v2"

document_analysis_client = DocumentIntelligenceClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

# Make sure your document's type is included in the list of document types the custom model can analyze
doc=r"Reali\sdo\sdo_1.png"
with open(doc, "rb") as f:
        base64_encoded_pdf = base64.b64encode(f.read()).decode("utf-8")

analyze_request = {
        "base64Source": base64_encoded_pdf
    }
poller = document_analysis_client.begin_analyze_document(model_id, analyze_request=analyze_request)
result = poller.result()

# iterate over tables, lines, and selection marks on each page
for item in result.documents:
        for k in item.fields:
            if "content" in item.fields[k].keys():
                print(f"Chiave: {k} Valore: {item.fields[k]["content"]}") 
            else:
                print(f"Chiave: {k} Valore: Non Trovato") 
